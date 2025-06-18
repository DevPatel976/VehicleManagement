from alembic import op
import sqlalchemy as sa
revision = '71a8e10b8da1'
down_revision = '74bd1a41d075'
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_reversed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('reversed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('reversal_reason', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('reversal_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('vehicle_registration', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('drivers_license', sa.String(length=20), nullable=True))
def downgrade():
    with op.batch_alter_table('reservations', schema=None) as batch_op:
        batch_op.drop_column('drivers_license')
        batch_op.drop_column('vehicle_registration')
        batch_op.drop_column('reversal_notes')
        batch_op.drop_column('reversal_reason')
        batch_op.drop_column('reversed_at')
        batch_op.drop_column('is_reversed')