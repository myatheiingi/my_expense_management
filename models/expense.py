from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EmployeeExpense(models.Model):
    _name = 'employee.expense'
    _description = 'Employee Expense'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Expense Name',
        required=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self._default_employee(),
    )

    category = fields.Selection(
        [
            ('travel', 'Travel'),
            ('food', 'Food'),
            ('office', 'Office Supplies'),
            ('transport', 'Transportation'),
            ('other', 'Other'),
        ],
        string='Category',
        required=True,
        default='other',
    )

    date = fields.Date(
        string='Expense Date',
        required=True,
        default=fields.Date.today,
    )

    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    description = fields.Text(
        string='Description',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Status',
        default='draft',
        required=True,
    )

    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
    )

    @api.model
    def _default_employee(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)],
            limit=1,
        )
        return employee.id

    @api.constrains('amount')
    def _check_amount(self):
        for expense in self:
            if expense.amount <= 0:
                raise ValidationError(
                    _('Expense amount must be greater than zero.')
                )

    def action_submit(self):
        for expense in self:
            if expense.state != 'draft':
                raise UserError(
                    _('Only draft expenses can be submitted.')
                )

            expense.state = 'submitted'

    def action_approve(self):
        if not self.env.user.has_group(
            'my_expense_management.group_expense_manager'
        ):
            raise UserError(
                _('Only Expense Managers can approve expenses.')
            )

        for expense in self:
            if expense.state != 'submitted':
                raise UserError(
                    _('Only submitted expenses can be approved.')
                )

            expense.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
            })

    def action_reject(self):
        if not self.env.user.has_group(
            'my_expense_management.group_expense_manager'
        ):
            raise UserError(
                _('Only Expense Managers can reject expenses.')
            )

        for expense in self:
            if expense.state != 'submitted':
                raise UserError(
                    _('Only submitted expenses can be rejected.')
                )

            expense.write({
                'state': 'rejected',
                'approved_by': self.env.user.id,
            })

    def action_reset(self):
        for expense in self:
            if expense.state not in ('rejected', 'submitted'):
                raise UserError(
                    _('This expense cannot be reset.')
                )

            expense.write({
                'state': 'draft',
                'approved_by': False,
            })