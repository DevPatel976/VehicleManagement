from alembic import op
import sqlalchemy as sa
revision = 'ef98e1e3fe5f'
down_revision = '71a8e10b8da1'
branch_labels = None
depends_on = None
def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_blocked', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('blocked_reason', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('blocked_at', sa.DateTime(), nullable=True))
def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('blocked_at')
        batch_op.drop_column('blocked_reason')
        batch_op.drop_column('is_blocked')