from odoo import _, api, exceptions, fields, models, tools
from odoo.tools import pycompat, ustr, formataddr
from odoo.tools.misc import clean_context
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

class TicketModel(models.Model):
    _name = 'helpdeskticket.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_user_tickets(self):
        tickets = self.env['helpdeskticket.model'].search_count([('create_uid', '=', self.env.user.id)])
        if tickets:
            return int(tickets) if tickets else 0

    name = fields.Char(string="Ticket Id")
    description = fields.Char(string="Description")
    note = fields.Text(string="Notes")
    assigned_user = fields.Many2one('res.users', string="Assignee")
    client_email = fields.Char(string="Client Email",)
    client_name = fields.Char(string="Client Name",)
    company_id = fields.Many2one('res.company', string="Company")
    partner_id = fields.Many2one("res.partner", string="Customer", required=False)
    email_logs = fields.Many2many("mail.mail", string="Mails", readonly=True)
    category = fields.Many2one("helpdeskcategory.model", string="Category", required=False)
    sla_id = fields.Many2one('helpdesk.tracker.sla', string="SLA")
    duration = fields.Integer(string="Duration")# , compute="compute_ticket_duration")
    num_tickets = fields.Integer(string="Tickets", default= lambda self: self._get_user_tickets())
    color = fields.Integer('Color')
    file = fields.Binary('Upload Document')
    file_name = fields.Char('File name')
    sla_duration = fields.Char('SLA Duration')

    @api.onchange('sla_id')
    def onchange_sla_id(self):
        if self.sla_id.time_hours:
            hours = self.sla_id.time_hours if self.sla_id.time_hours else ""
            self.sla_duration = f'{self.sla_id.time_hours} Days, {hours} Hours'

    ticket_type = fields.Selection([('customer', 'Customer Centered'), ('issue', 'Issue'), ('other', 'Others')], default='issue', string="Ticket Type")
    priority = fields.Selection([('high', 'High'), ('low', 'Low'), ('medium', 'Medium')], default='low', string="Priority")
    status = fields.Selection([('new', 'New'), ('open', 'Open'), ('close', 'Closed')], default='new', string="Status")
    expected_date = fields.Datetime(string='Deadline Date')
    write_ids = fields.Many2many('res.users', string="Modifiers")
    stage_id = fields.Many2one('helpdeskstages.model', string="Stages")
    active = fields.Boolean(string="Active", default=True)
    close_ticket = fields.Boolean(string="Closed", default=False)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('helpdeskticket.model')
        vals['name'] = sequence or '/'
        return super(TicketModel, self).create(vals)
        
    def write(self, vals):
        res = super(TicketModel, self).write(vals)
        vals['write_ids']= [(4, self.env.user.id)]
        return res

    def action_submit(self):
        self.status = 'open'
        self.send_stage_notification()

    @api.onchange('category')
    def _get_stages(self):
        for rec in self:
            if rec.category:
                lists = []
                stage_ids = self.env['helpdeskstages.model'].search([])
                sla_ids = self.env['helpdesk.tracker.sla'].search([('category_id', '=', rec.category.id)])
                for stg in stage_ids:
                    categ_ids = stg.mapped('apply_on').filtered(lambda s: s.id == self.category.id)
                    if categ_ids:
                        lists.append(stg.id)
                domain = {'stage_id': [('id', 'in', lists)], 'sla_id': [('id', 'in', [sla.id for sla in sla_ids])]}
                return {'domain': domain}

    @api.onchange('stage_id')
    def move_stage_action(self):
        self.send_stage_notification()

    def toggle_close_ticket_action(self):
        for rec in self: 
            status = True if not rec.close_ticket else False
            body = "Dear {0}, <br/>This is to inform you that ticket with ID {1}\
                 have been {2}. Kindly Confirm by replying to this mail.<br/>\
                 Regards".format(rec.client_name, rec.name, status)
            rec.close_ticket = status
            mail_id = rec.send_mail(self.env.user.email, self.client_email, False, body, False)
            rec.write({
                'email_logs': [(4, mail_id.id)]
            })

    def assign_issue(self):
        for rec in self:
            rec.assigned_user = self.env.user.id
            body = "Dear {0}, <br/>This is to inform you that ticket with ID {1}\
                 is in progress and have been assigned to - {2}.<br/>\
                 Regards".format(rec.client_name, rec.name, rec.assigned_user.name)
            mail_id = self.send_mail(self.env.user.email, self.client_email, body, False) 
            rec.write({
            'email_logs': [(4, mail_id.id)], 'status': 'open',
            })

    def send_stage_notification(self):
        for rec in self: 
            user = self.env.user.name
            body = f"Dear {rec.client_name}, <br/>This is to inform you that ticket with ID {rec.name}\
                 is moved to {rec.stage_id.name or 'progress'} by {user}.<br/>\
                 Regards"
            mail_id = self.send_mail(self.env.user.email, self.client_email, body, False) 
            rec.update({
            'email_logs': [(4, mail_id.id)]
            })

    def all_my_tickets(self):
        return self.get_my_ticket_action_record()

    def toggle_active(self):
        self.active = True if self.active == False else False  

    @api.onchange('category')
    def compute_ticket_deadline(self):
        current_date = datetime.now()
        if self.category:
            duration = self.category.highest_duration
            end_time = current_date + timedelta(days=duration)
            self.expected_date = end_time

    def validate_and_get_email(self):
        email_to = None
        if self.client_email:
            email_to = self.client_email

        if self.partner_id and not self.partner_id.email:
            raise ValidationError('The selected partner does not have an email configured')
        else:
            email_to = self.partner_id.email
        return email_to

    def send_by_mail_button(self):
        if not self.category:
            raise ValidationError("Please select a category")
        body = f"Hi {self.client_name}, your ticket with ID {self.name} is currently been handled. The status is: {self.stage_id.name} \n Thanks"
        mail_id = self.send_mail(self.env.user.email, self.client_email, body, False)
        self.write({
            'email_logs': [(4, mail_id.id)]
        })

    def send_mail(self, email_from, mail_to, body, attachment=None):
        # email_template = self.env.ref('helpdesk_api.send_helpdesk_email_template')
        # """args: inform_internal_users determines if the mail is sent to users who picks up the ticket"""
        # body = email_template.body_html
        #  if inform_internal_users else custom_body if custom_body else "Ticket have been generated with ID # {}".format(self.name)
        subject_msg = self.name # if not client_send else self.category.auto_msgs() 
        subject = "HELPDESK NOTIFICATION #{}".format(subject_msg)
        recipients = [rec.login for rec in self.category.mapped('user_ids')]
        mail_data = {
            'email_from': email_from,
            'subject': subject,
            'email_to': mail_to,
            'email_cc': ','.join(recipients) if False not in recipients else False,
            'body_html': body,
        }
        mail_id = self.env['mail.mail'].create(mail_data)
        return mail_id 
        
        # self.env['mail.mail'].send(mail_id)
 
    def get_record_reference(self):
        reference_id = self.env['helpdeskticket.model'].search([('id', '=', self.id)])
        if not reference_id:
            raise ValidationError('There is no related record found!.')
        resp = {
            'type': 'ir.actions.act_window',
            'name': _('Reference'),
            'res_model': 'helpdeskticket.model',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': reference_id.id
        }
        return resp

    def _get_action(self, action_form_xmlid, action_tree_xmlid):
        tree_view_ref = self.env.ref(action_tree_xmlid, False)
        form_view_ref = self.env.ref(action_form_xmlid, False)
        domain = None
        helpdesk_all = self.env['helpdeskticket.model'].search([('assigned_user', '=', self.env.user.id), ('write_ids', 'in', [self.assigned_user.id])])
        return {
            'domain': [('id', 'in', [rec.id for rec in helpdesk_all])],
            'name': 'My Tickets',
            'res_model': 'helpdeskticket.model',
            'type': 'ir.actions.act_window',
            'views': [(tree_view_ref.id, 'tree'),(form_view_ref.id, 'form')],
        } 

    # @api.multi
    def get_my_ticket_action_record(self):
        return self._get_action('helpdesk_api.helpdeskticket_view_form', 'helpdesk_api.helpdesktickets_view_tree')

