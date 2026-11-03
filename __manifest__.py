{
    'name': 'My Expense Management',
    'version': '19.0.1.0.0',
    'summary': 'Employee Expense Submission and Approval',
    'category': 'Human Resources',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': ['hr'],
    'data': [
        'security/expense_security.xml',
        'security/ir.model.access.csv',
        'views/expense_views.xml',
    ],
    'application': True,
    'installable': True,
}