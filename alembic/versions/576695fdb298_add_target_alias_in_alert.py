"""add target alias in alert

Revision ID: 576695fdb298
Revises: f81e0a7329a0
Create Date: 2023-11-04 23:25:51.990308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "576695fdb298"
down_revision: Union[str, None] = "f81e0a7329a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("alerts", sa.Column("target_alias", sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("alerts", "target_alias")
    # ### end Alembic commands ###