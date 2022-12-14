##############################################################################
#    Copyright (C) 2021. All Rights Reserved
#    Maach / QIS Solutions

{
    'name': 'ETQA',
    'version': '1.5',
    'author': "Maduka Chris Sopulu / QIS Solution",
    'summary': 'MIS ETQA MODULE',
    'depends': ['inseta_skills', 'project'],
    'description': "MIS ETQA MODULE",
    "data": [
            'security/security_view.xml',
            'security/ir.model.access.csv',
            'data/mail_templates.xml',
            'data/data.xml',
            'data/automated_action.xml',
            'data/quality_assurance_data.xml',
            'sequence/sequence.xml',
            'wizard/inseta_etqa_wizard.xml',
            'wizard/inseta_learner_wizard.xml',
            'wizard/inseta_etqa_reject_wizard.xml',
            'views/inseta_provider_accreditation_view.xml',
            'views/inseta_assessor_register_view.xml',
            'views/inseta_assessor_view.xml',
            'views/inseta_moderator_view.xml',
            'views/inseta_provider.xml',
            'views/inseta_moderator_register_view.xml',
            'views/inseta_qualification_view.xml',
            'views/inseta_unit_standard_view.xml',
            'views/inseta_learner_register.xml',
            'views/inseta_assessment_view.xml',
            'views/inseta_learnership_assessment_view.xml',
            'views/inseta_learner_learnership_view.xml',
            'views/inseta_learner.xml',
            'views/inseta_learner_programme_2.xml',
            'views/inseta_learner_programme.xml',
            'views/inseta_report.xml',
            'wizard/learner_batch_upload_view.xml',
            'wizard/inseta_programme_register_wizard.xml',
            'wizard/inseta_batch_certificate_report.xml',
            'security/ir_rule.xml',
            'reports/moderator_appointment_letter.xml',
            'reports/moderator_statement_of_result.xml',
            'reports/assessor_appointment_letter.xml',
            'reports/assessor_statement_of_result.xml',
            'reports/assessor_rejection_letter.xml',
            'reports/moderator_rejection_letter.xml',
            'reports/learner_appointment_letter.xml',
            'reports/learner_rejection_letter.xml',
            'reports/certificate_assessment_general_report.xml',
            'reports/certificate_assessment_report_template.xml',
            'reports/batch_certificate_report_template.xml',
            'reports/certificate_provider.xml',
            'reports/certificate_provider_accreditation.xml',
            'reports/certificate_moderator.xml',
            'reports/certificate_assessor.xml',
            'reports/certificate_qualification_learnership.xml',
            'reports/certificate_skills_learnership.xml',
            'reports/certificate_learner_learnership.xml',
            'reports/statement_of_result_qualification.xml',
            'reports/statement_of_result_learnership.xml',
            'reports/statement_of_results_skills.xml',
            'reports/programme_certificate_report_template.xml',
            'reports/provider_accreditation_statement_summary.xml',
            'data/programme_status.xml',
    ],
    'css': [],
    'js': [],
    'qweb': [],
    "active": False,
    'application': True,
    "sequence": 3
}
