"""Initial database schema
Revision ID: 001
Revises:
Create Date: 2026-05-15
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sys_role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column("is_system", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "sys_user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("is_superuser", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "sys_department",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.ForeignKeyConstraint(["parent_id"], ["sys_department.id"]),
    )
    op.create_table(
        "sys_employee",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_number", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(100), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("id_card", sa.String(18), nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("hire_date", sa.Date(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("position", sa.String(100), nullable=True),
        sa.Column("employment_status", sa.String(20), default="active"),
        sa.Column("address", sa.String(255), nullable=True),
        sa.Column("emergency_contact", sa.String(100), nullable=True),
        sa.Column("emergency_phone", sa.String(20), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_number"),
        sa.ForeignKeyConstraint(["department_id"], ["sys_department.id"]),
    )
    op.create_table(
        "sys_salary",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("base_salary", sa.Numeric(12, 2), default=0),
        sa.Column("bonus", sa.Numeric(12, 2), default=0),
        sa.Column("deductions", sa.Numeric(12, 2), default=0),
        sa.Column("tax", sa.Numeric(12, 2), default=0),
        sa.Column("allowances", sa.Numeric(12, 2), default=0),
        sa.Column("net_salary", sa.Numeric(12, 2), default=0),
        sa.Column("pay_month", sa.Date(), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("payment_status", sa.String(20), default="pending"),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["employee_id"], ["sys_employee.id"]),
    )
    op.create_table(
        "sys_user_role",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["sys_role.id"]),
    )


def downgrade() -> None:
    op.drop_table("sys_user_role")
    op.drop_table("sys_salary")
    op.drop_table("sys_employee")
    op.drop_table("sys_department")
    op.drop_table("sys_user")
    op.drop_table("sys_role")
