"""empty message

Revision ID: 63d3db5bd622
Revises: 
Create Date: 2023-06-16 10:11:42.068381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63d3db5bd622'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('diagnostics_metastasis_search',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('main_diagnosis_primary_tumor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('patient',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('gender', sa.String(length=10), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('op_date_primary_tumor', sa.Date(), nullable=True),
    sa.Column('age_at_OP', sa.String(length=10), nullable=True),
    sa.Column('BMI', sa.String(length=10), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('height', sa.Float(), nullable=True),
    sa.Column('pre_existing_conditions', sa.String(length=10), nullable=True),
    sa.Column('cardiac_diseases', sa.String(length=10), nullable=True),
    sa.Column('pulmonary_diseases', sa.String(length=10), nullable=True),
    sa.Column('urological_diseases', sa.String(length=10), nullable=True),
    sa.Column('endocrine_diseases', sa.String(length=10), nullable=True),
    sa.Column('previous_vascular_diseases', sa.String(length=10), nullable=True),
    sa.Column('tumor_side', sa.String(length=10), nullable=True),
    sa.Column('tumor_marker_CEA', sa.String(length=50), nullable=True),
    sa.Column('tumor_marker_CA19_9', sa.String(length=50), nullable=True),
    sa.Column('preoperative_endoscopy', sa.String(length=20), nullable=True),
    sa.Column('surgical_procedure', sa.String(length=30), nullable=True),
    sa.Column('localization_OP', sa.String(length=10), nullable=True),
    sa.Column('T_stadium', sa.String(length=10), nullable=True),
    sa.Column('N_stadium', sa.String(length=10), nullable=True),
    sa.Column('UICC_Stadium', sa.String(length=10), nullable=True),
    sa.Column('grading', sa.String(length=10), nullable=True),
    sa.Column('lymphangiosis_carcinomatous', sa.String(length=10), nullable=True),
    sa.Column('vascular_invasion', sa.String(length=10), nullable=True),
    sa.Column('perineural_invasion', sa.String(length=10), nullable=True),
    sa.Column('tumor_diameter_in_cm', sa.String(length=10), nullable=True),
    sa.Column('progression_free_survival_in_months', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('treatment_chemotherapy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('patient_treatment',
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('treatment_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ),
    sa.ForeignKeyConstraint(['treatment_id'], ['treatment_chemotherapy.id'], ),
    sa.PrimaryKeyConstraint('patient_id', 'treatment_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('patient_treatment')
    op.drop_table('treatment_chemotherapy')
    op.drop_table('patient')
    op.drop_table('main_diagnosis_primary_tumor')
    op.drop_table('diagnostics_metastasis_search')
    op.drop_table('admin')
    # ### end Alembic commands ###
