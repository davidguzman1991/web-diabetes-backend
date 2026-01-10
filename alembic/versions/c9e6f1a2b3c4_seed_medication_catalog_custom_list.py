"""seed medication catalog custom list

Revision ID: c9e6f1a2b3c4
Revises: b7c1d2e3f4a5
Create Date: 2026-01-10 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "c9e6f1a2b3c4"
down_revision = "b7c1d2e3f4a5"
branch_labels = None
depends_on = None


SEED_NAMESPACE = uuid.UUID("3c4c2c2b-1b11-4d6f-8c9b-6a5f7b0f6d39")

MEDICATIONS = [
    "Jardiance Duo 850/12.5 mg (Metformina / Empagliflozina) Comprimidos recubiertos",
    "Jardiance Duo 1000/12.5 mg (Metformina / Empagliflozina) Comprimidos recubiertos",
    "Jardiance 10 mg (Empagliflozina) Comprimidos recubiertos",
    "Fanter 10 mg (Dapagliflozina) Comprimidos recubiertos",
    "Firialta 10 mg (Finerenona) Comprimidos recubiertos",
    "Firialta 20 mg (Finerenona) Comprimidos recubiertos",
    "Glicenex SR 1000 mg (Metformina Clorhidrato) Comprimidos Liberación Prolongada",
    "Glicenex SR 500 mg (Metformina Clorhidrato) Comprimidos Liberación Prolongada",
    "Glicenex SR 750 mg (Metformina Clorhidrato) Comprimidos Liberación Prolongada",
    "Galvus 50 mg (Vildagliptina) Comprimidos recubiertos",
    "Galvus Met 500 / 50 mg (Metformina / Vildagliptina) Comprimidos recubiertos",
    "Galvus Met 850 / 50 mg (Metformina / Vildagliptina) Comprimidos recubiertos",
    "Galvus Met 1000 / 50 mg (Metformina / Vildagliptina) Comprimidos recubiertos",
    "Trayenta 5 mg (Linagliptina) Comprimidos recubiertos",
    "Trayenta Duo 2.5 / 500 mg (Linagliptina / Metformina) Comprimidos recubiertos",
    "Trayenta Duo 2.5 / 850 mg (Linagliptina / Metformina) Comprimidos recubiertos",
    "Trayenta Duo 2.5 / 1000 mg (Linagliptina / Metformina) Comprimidos recubiertos",
    "Colesta 20 mg (Rosuvastatina) Comprimidos recubiertos",
    "Colesta 10 mg (Rosuvastatina) Comprimidos recubiertos",
    "Rumada 10 / 10 (Rosuvastatina + Ezetimiba) Comprimidos recubiertos",
    "Rumada 20 / 10 (Rosuvastatina + Ezetimiba) Comprimidos recubiertos",
    "Ozempic Dual Dose (Semaglutida) Soluc. Inyect. Pluma Precargada 2 mg / 1.5 ml",
    "Ozempic Fix Dose (Semaglutida) Soluc. Inyect. Pluma Precargada 4 mg / 3 ml",
    "Tresiba Flextouch (insulina degludec) Sol. Inyectable 1X3 ml",
    "Apidra Solostar (insulina glulisina) Sol. Inyectable. 100 UI Dispos. 3 ml",
    "Humalog Kwikpen (Insulina lispro) Sol. Inyectable. 100 UI/ml",
    "Lantus Solostar (insulina glargina) Sol. Inyectable. 100 UI Dispos.3 Ml",
    "Toujeo (insulina glargina U300) Sol Inyect (Lapiz Aplicador) 300 U/Ml",
    "GenneoS Xr (Metformina / Sitagliptina) 1000 mg / 50 mg Tabletas recubiertas",
    "GenneoS Xr (Metformina / Sitagliptina) 500 mg / 50 mg Tabletas recubiertas",
    "GenneoS Xr (Metformina / Sitagliptina) 850 mg / 50 mg Tabletas recubiertas",
    "GenneoS Xr (Metformina / Sitagliptina) 1000 mg / 100 mg Tabletas recubiertas",
    "Indivan 40 mg (Telmisartan) Comprimidos recubiertos",
    "Indivan forte 80 mg (Telmisartan) Comprimidos recubiertos",
    "Telsar 40 mg (Telmisartan) Comprimidos recubiertos",
    "Telsar AM 80 / 5 mg (Telmisartan / Amlodipino) Comprimidos recubiertos",
    "Telsar Hc 80 / 12.5 mg (Telmisartan / Hidroclorotiazida) Comprimidos recubiertos",
    "Milpax (Alginato de sodio / Bicarbonato de sodio) Suspension oral",
    "Endial Digest (cinitaprida 1mg, Simeticona 200mg, Pancreatina 8xUSP 100mg) Comprimidos recubiertos",
    "Ulcozol rapid (Omeprazol 20 mg /Bicarbonato de sodio 1680 mg) Sobres. polvo para restituir",
    "Ulcozol rapid (Omeprazol 20 mg /Bicarbonato de sodio 1110 mg) capsulas",
    "Analgan Rapid 500 mg (Paracetamol) Capsula Blanda",
    "Palexis Retard 50 mg (Tapentadol) Tabletas recubiertas de liberación prolongada",
    "Palexis Retard 100 mg (Tapentadol) Tabletas recubiertas de liberación prolongada",
    "Palexis 50 mg (Tapentadol) Tabletas",
    "Prestat 50 mg (pregabalina) Comprimidos recubiertos",
    "Prestat 75 mg (pregabalina) Comprimidos recubiertos",
    "Prestat 150 mg (pregabalina) Comprimidos recubiertos",
    "Realta 30 mg (Duloxetina) Capsulas",
    "Realta 60 mg (Duloxetina) Capsulas",
    "Celtium 10 mg (Escitalopram) Comprimidos recubiertos",
    "Celtium 20 mg (Escitalopram) Comprimidos recubiertos",
    "Ibuprofeno 400 mg tabletas",
    "Ibuprofeno 600 mg tabletas",
    "Gabapentina 300 mg capsulas",
    "Dolo Neurobion forte (Diclofenaco sodico / Vitamina B1 - B6 - B12) tabletas",
    "Fontactiv Diabest (Proteína de suero de leche, minerales, Vitaminas) Suplemento Polvo",
    "Nepro Bp Vainilla 1,8 Kcal 220 Ml (suplemento bajo en proteína para personas en pre diálisis) liquido oral",
    "Nepro Ap Vainilla 1,8 Kcal 220 Ml (suplemento Alto en proteína para personas en diálisis) liquido oral",
    "Urea 10% (Crema Hidratante)",
    "Amoxicilina + Acido Clavulanico. 1gr (875 / 125 mg) Tabletas",
    "Doxiciclina 100 mg Tabletas",
    "Ceftriaxona 1gr. Solucion inyectable",
    "Piperacilina / Tazobactam 4.5 gr polvo para inyeccion",
    "Cloruro de sodio 0.9% 1000 ml. Solucion inyectable",
    "Cloruro de sodio 0.9% 500 ml. Solucion inyectable",
    "Cloruro de sodio 0.9% 250 ml. Solucion inyectable",
    "Omacor (Omega-3) 1000 mg (EPA etil éster 460 mg + DHA etil éster 380 mg) Capsulas blandas",
    "Eutirox 50 mcg (Levotiroxina) tabletas",
    "Eutirox 75 mcg (Levotiroxina) tabletas",
    "Eutirox 88 mcg (Levotiroxina) tabletas",
    "Eutirox 100 mcg (Levotiroxina) tabletas",
    "Eutirox 112 mcg (Levotiroxina) tabletas",
    "Eutirox 125 mcg (Levotiroxina) tabletas",
    "Vitamina B12 1000 Mcg Tableta Recubierta",
    "Tioctan 600 mg (Ácido Tióctico) Comprimidos recubiertos",
]


def upgrade() -> None:
    conn = op.get_bind()
    for nombre in MEDICATIONS:
        med_id = uuid.uuid5(SEED_NAMESPACE, nombre)
        conn.execute(
            sa.text(
                "insert into medication_catalog (id, nombre_generico, presentacion, forma, activo) "
                "select :id, :nombre, null, null, true "
                "where not exists ("
                "select 1 from medication_catalog "
                "where lower(nombre_generico) = lower(:nombre)"
                ")"
            ),
            {"id": med_id, "nombre": nombre},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for nombre in MEDICATIONS:
        med_id = uuid.uuid5(SEED_NAMESPACE, nombre)
        conn.execute(
            sa.text("delete from medication_catalog where id = :id"),
            {"id": med_id},
        )
