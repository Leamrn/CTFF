#Import
from flask import Flask, render_template, request, redirect, flash, session
from flask import render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash
import matplotlib.pyplot as plt
import json
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
import math
from sqlalchemy import text
from sqlalchemy import or_
import pandas as pd
from datetime import datetime
from flask import jsonify, request

app = Flask(__name__, static_folder='assets')




# database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 300}
app.secret_key = 'your_secret_key' # Clé secrète pour les sessions

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definition of the intermediate association table
patient_treatment = db.Table('patient_treatment',
    db.Column('patient_id', db.Integer, db.ForeignKey('patient.id'), primary_key=True),
    db.Column('treatment_id', db.Integer, db.ForeignKey('treatment_chemotherapy.id'), primary_key=True)
)

### Check if an administrator exists in the database

# Check if an administrator exists in the database
def has_admin():
    return db.session.query(Admin).first() is not None

###Class definition

# Definition of the TreatmentChemotherapy class
class TreatmentChemotherapy(db.Model):
    __tablename__ = 'treatment_chemotherapy'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="", unique=True)

# Definition of the Patient class
class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    #personal info
    first_name = db.Column(db.String(50), default="")
    last_name = db.Column(db.String(50), default="")
    gender = db.Column(db.String(10), default="")
    date_of_birth = db.Column(db.Date, default=None)
    email = db.Column(db.String(100), default="")
    op_date_primary_tumor = db.Column(db.Date, default=None)
    age_at_OP = db.Column(db.String(10), default="")
    BMI = db.Column(db.String(10), default="")
    weight = db.Column(db.Float, default=None)
    height = db.Column(db.Float, default=None)
    #medical info
    pre_existing_conditions = db.Column(db.String(10), default="")
    cardiac_diseases= db.Column(db.String(10), default="")
    pulmonary_diseases= db.Column(db.String(10), default="")
    urological_diseases= db.Column(db.String(10), default="")
    endocrine_diseases= db.Column(db.String(10), default="")
    previous_vascular_diseases= db.Column(db.String(10), default="")
    #About the tumor
    tumor_side = db.Column(db.String(10), default="")
    tumor_marker_CEA = db.Column(db.String(50), default="")
    tumor_marker_CA19_9 = db.Column(db.String(50), default="")
    preoperative_endoscopy = db.Column(db.String(20), default="")
    surgical_procedure= db.Column(db.String(30), default="")
    localization_OP= db.Column(db.String(10), default="")
    T_stadium= db.Column(db.String(10), default="")
    N_stadium= db.Column(db.String(10), default="")
    UICC_Stadium= db.Column(db.String(10), default="")
    grading= db.Column(db.String(10), default="")
    lymphangiosis_carcinomatous= db.Column(db.String(10), default="")
    vascular_invasion= db.Column(db.String(10), default="")
    perineural_invasion= db.Column(db.String(10), default="")
    tumor_diameter_in_cm= db.Column(db.String(10), default="")
    #treatment
    progression_free_survival_in_months= db.Column(db.String(10), default="")
    treatments = db.relationship('TreatmentChemotherapy', secondary='patient_treatment', backref='patients')

### We not use this part for the moment
# Definition of the main_diagnosis_primary_tumor class
class main_diagnosis_primary_tumor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="", unique=True)

#main_diagnosis_primary_tumor

main_diagnosis_primary_tumor1 = main_diagnosis_primary_tumor(name='Zökumkarzinom')
main_diagnosis_primary_tumor2 = main_diagnosis_primary_tumor(name='Colon ascendens Karzinom')
main_diagnosis_primary_tumor3 = main_diagnosis_primary_tumor(name='Colonkarzinom re. Flexur')
main_diagnosis_primary_tumor4 = main_diagnosis_primary_tumor(name='Karzinom des Colon transversum')
main_diagnosis_primary_tumor5 = main_diagnosis_primary_tumor(name='Karzinom in der linken Kolonflexur')
main_diagnosis_primary_tumor6 = main_diagnosis_primary_tumor(name='Colon descendens-Karzinom')
main_diagnosis_primary_tumor7 = main_diagnosis_primary_tumor(name='Sigma-Karzinom')
main_diagnosis_primary_tumor9 = main_diagnosis_primary_tumor(name='Rektum-Karzinom, oberes Drittel')
main_diagnosis_primary_tumor10 = main_diagnosis_primary_tumor(name='Rektum Karzinom, unteres Drittel')
main_diagnosis_primary_tumor11 = main_diagnosis_primary_tumor(name='Colon transversum-Karzinom, rechte Flexur')


class diagnostics_metastasis_search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), default="", unique=True)

#diagnostics_metastasis_search

diagnostics_metastasis_search1 = diagnostics_metastasis_search(name='CT Abdomen')
diagnostics_metastasis_search2 = diagnostics_metastasis_search(name='Sono Abdomen')
diagnostics_metastasis_search3 = diagnostics_metastasis_search(name='MRT Abdomen')
diagnostics_metastasis_search4 = diagnostics_metastasis_search(name='CT Thorax')
diagnostics_metastasis_search5 = diagnostics_metastasis_search(name='Sono Abdomen, CT Thorax')
diagnostics_metastasis_search6 = diagnostics_metastasis_search(name='nicht durchgeführt')
diagnostics_metastasis_search99 = diagnostics_metastasis_search(name='n/a')


###


### Functions associated with the index page

#index check is the user is connected or not
@app.route("/")
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/login')
    else:
        return render_template('index.html')

# Route to create an object and add it to the database

@app.route("/", methods=['POST'])
def create():

    #retrieve the data submitted in the form
    #personal info
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    gender = request.form['gender']
    date_of_birth_str = request.form['date_of_birth']
    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
    email = request.form['email']
    weight = request.form['weight']
    height = request.form['height']
    op_date_primary_tumor_str = request.form['op_date_primary_tumor']
    age_at_OP = request.form['age_at_OP']
    op_date_primary_tumor= datetime.strptime(op_date_primary_tumor_str, '%Y-%m-%d').date()
    BMI =request.form['BMI']
    BMI = float(BMI)
    print(BMI)
    #medical history
    pre_existing_conditions = request.form['pre_existing_conditions']
    cardiac_diseases= request.form['cardiac_diseases']
    pulmonary_diseases= request.form['pulmonary_diseases']
    urological_diseases= request.form['urological_diseases']
    endocrine_diseases= request.form['endocrine_diseases']
    previous_vascular_diseases= request.form['previous_vascular_diseases']
    #about the tumor
    tumor_side = request.form['tumor_side']
    tumor_marker_CEA = request.form['tumor_marker_CEA']
    tumor_marker_CA19_9 = request.form['tumor_marker_CA19_9']
    preoperative_endoscopy = request.form['preoperative_endoscopy']
    surgical_procedure= request.form['surgical_procedure']
    localization_OP= request.form['localization_OP']
    T_stadium= request.form['T_stadium']
    N_stadium= request.form['N_stadium']
    UICC_Stadium= request.form['UICC_Stadium']
    grading= request.form['grading']
    lymphangiosis_carcinomatous= request.form['lymphangiosis_carcinomatous']
    vascular_invasion= request.form['vascular_invasion']
    perineural_invasion= request.form['perineural_invasion']
    tumor_diameter_in_cm= request.form['tumor_diameter_in_cm']





    # create an instance of the Patient class with the submitted data
    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        date_of_birth=date_of_birth,
        email=email,
        weight=weight,
        height=height,
        op_date_primary_tumor = op_date_primary_tumor,
        age_at_OP = age_at_OP,
        BMI =BMI,
        pre_existing_conditions = pre_existing_conditions,
        pulmonary_diseases= pulmonary_diseases,
        urological_diseases= urological_diseases,
        endocrine_diseases= endocrine_diseases,
        previous_vascular_diseases= previous_vascular_diseases,
        cardiac_diseases=  cardiac_diseases,
        tumor_side = tumor_side,
        tumor_marker_CEA = tumor_marker_CEA,
        tumor_marker_CA19_9 = tumor_marker_CA19_9,
        preoperative_endoscopy = preoperative_endoscopy,
        surgical_procedure= surgical_procedure,
        localization_OP= localization_OP,
        T_stadium= T_stadium,
        N_stadium= N_stadium,
        UICC_Stadium= UICC_Stadium,
        grading= grading,
        lymphangiosis_carcinomatous= lymphangiosis_carcinomatous,
        vascular_invasion= vascular_invasion,
        perineural_invasion= perineural_invasion,
        tumor_diameter_in_cm= tumor_diameter_in_cm,
        )





    # add the new patient to the database
    db.session.add(patient)
    db.session.commit()
    #Find the best treatment
    result = trouver_meilleur_traitement(patient)

    #Create the graph
    if result:
        patient_id = patient.id
        traitement_id = result[0][0].id
        trait_graph = [result[0][0].name,result[2][0][0].name,result[2][2][0].name ]
        result_graph = [result[1],result[2][1], result[2][3]]
        trait_graph_json = [json.dumps(element) for element in trait_graph]
        result_graph_json = [json.dumps(element) for element in result_graph]

        result = result[0][0].name

        plt.figure(figsize=(13, 4))
        plt.style.use('seaborn')
        plt.plot(trait_graph, result_graph, marker='o')
        plt.xlabel('Treatments')
        plt.ylabel('Mean in months of survival')
        plt.title('Treatment comparaison')

        # Adjust margins
        plt.subplots_adjust(left=0.05, bottom=0.2)
        #Save the image
        plt.savefig('assets/graph.png')

        # show the graph
        plt.show()

    else:
        # If any treatment is found
        patient_id = None
        traitement_id = None

    return render_template('result.html' , patient=patient, result=result, patient_id=patient_id, traitement_id=traitement_id, trait_graph_json=trait_graph_json,result_graph_json=result_graph_json)

###Don't use this function
@app.route('/associer', methods=['POST'])
def associer_traitement():
    patient_id = request.form['patient_id']
    traitement_id = request.form['traitement_id']
    valider = request.form['valider']
    patient = Patient.query.get(patient_id)
    treatment = TreatmentChemotherapy.query.get(traitement_id)
    if valider == 'true':
        if treatment != None:
            patient.treatments.append(treatment)
            db.session.commit()
        return redirect('/admin')
    else:
        return redirect('/admin')
###
if __name__ == '__main__':
    app.run()

#Find the best treatment


def trouver_meilleur_traitement(patient):

    #Treatment creation if we need it
    treatment1 = TreatmentChemotherapy.query.filter_by(name='Capecitabin mono or 5-FU/FA').first()
    treatment2 = TreatmentChemotherapy.query.filter_by(name='Folfox 4 or Folfox 6 or Xelox').first()
    treatment3 = TreatmentChemotherapy.query.filter_by(name='Xelox + Bevacizumab or CapIri + Bevacizumab').first()
    treatment = TreatmentChemotherapy.query.filter_by(name='None').first()

    if not treatment1:
        treatment1 = TreatmentChemotherapy(name='Capecitabin mono or 5-FU/FA')
        db.session.add(treatment1)

    if not treatment2:
        treatment2 = TreatmentChemotherapy(name='Folfox 4 or Folfox 6 or Xelox')
        db.session.add(treatment2)

    if not treatment3:
        treatment3 = TreatmentChemotherapy(name='Xelox + Bevacizumab or CapIri + Bevacizumab')
        db.session.add(treatment3)

    if not treatment:
        treatment = TreatmentChemotherapy(name='None')
        db.session.add(treatment)

    db.session.commit()

    # Retrieve patient information
    tumor_diameter_in_cm = patient.tumor_diameter_in_cm
    gender = patient.gender
    BMI = patient.BMI
    pre_existing_conditions = patient.pre_existing_conditions
    pulmonary_diseases = patient.pulmonary_diseases
    urological_diseases = patient.urological_diseases
    endocrine_diseases= patient.endocrine_diseases
    previous_vascular_diseases= patient.previous_vascular_diseases
    tumor_marker_CA19_9= patient.tumor_marker_CA19_9
    tumor_marker_CEA=patient.tumor_marker_CEA
    age_at_OP = patient.age_at_OP
    T_stadium= patient.T_stadium
    N_stadium= patient.N_stadium
    UICC_Stadium= patient.UICC_Stadium
    grading= patient.grading
    lymphangiosis_carcinomatous= patient.lymphangiosis_carcinomatous
    vascular_invasion= patient.vascular_invasion
    perineural_invasion= patient.perineural_invasion


    # database search to retrieve similar patient profiles
    #criteria_list is a list with all the criteria we use to choose the best treatment
    criteria_list = []
    criteria_list.append(Patient.BMI == BMI)
    criteria_list.append(Patient.pre_existing_conditions == pre_existing_conditions)
    criteria_list.append(Patient.previous_vascular_diseases == previous_vascular_diseases)
    criteria_list.append(Patient.endocrine_diseases == endocrine_diseases)
    criteria_list.append(Patient.urological_diseases == urological_diseases)
    criteria_list.append(Patient.pulmonary_diseases == pulmonary_diseases)
    criteria_list.append(Patient.T_stadium== T_stadium)
    criteria_list.append(Patient.N_stadium == N_stadium)
    criteria_list.append(Patient.UICC_Stadium == UICC_Stadium)
    criteria_list.append(Patient.grading == grading)

    #database search to retrieve similar patient profiles

    if tumor_marker_CA19_9 != 'CA19_9 not determined':
        criteria_list.append(Patient.tumor_marker_CA19_9 == tumor_marker_CA19_9)

    if tumor_marker_CEA != 'CEA not determined':
        criteria_list.append(Patient.tumor_marker_CEA == tumor_marker_CEA)

    if lymphangiosis_carcinomatous != 'n/a':
        criteria_list.append(Patient.lymphangiosis_carcinomatous == lymphangiosis_carcinomatous)

    if vascular_invasion != 'n/a':
        criteria_list.append(Patient.vascular_invasion == vascular_invasion)

    if perineural_invasion != 'n/a':
        criteria_list.append(Patient.perineural_invasion == perineural_invasion)


    patients_similaires = Patient.query.filter(or_(*criteria_list)).all()

    meilleur_traitement = None
    meilleur_resultat = 0

    list_treatment= []
    list_result=[]
    for patient_similaire in patients_similaires:
        if patient_similaire.progression_free_survival_in_months != "":
            list_treatment.append(patient_similaire.treatments)
            list_result.append(patient_similaire.progression_free_survival_in_months)
    # Retrieve the positions of treatment in the list
    positions1 = []
    positions2 = []
    positions3 = []
    for i, sublist in enumerate(list_treatment):
        for j,treatment in enumerate(sublist):
            if treatment == treatment1:
                positions1.append((i, j))

    for i, sublist in enumerate(list_treatment):
        for j,treatment in enumerate(sublist):
            if treatment == treatment2:
                positions2.append((i,j))

    for i, sublist in enumerate(list_treatment):
        for j,treatment in enumerate(sublist):
            if treatment == treatment3:
                positions3.append((i,j))

    #With calculate the average of survival
    result1 = 0
    # show the position
    for position in positions1:
        result1 += float(list_result[int(position[0])])
    if len(positions1) != 0:
        result1 = result1 / len(positions1)



    result2 = 0
    for position in positions2:
        result2 += float(list_result[int(position[0])])
    if len(positions2) != 0:
        result2 = result2 / len(positions2)

    result3 = 0
    for position in positions3:
        result3 += float(list_result[int(position[0])])
    if len(positions3) != 0:
        result3 = result3 / len(positions3)

    #Find the best result
    maximum = max(result1, result2, result3)
    if result1 == 0 and result2 == 0 and result3 == 0:
        meilleur_traitement = TreatmentChemotherapy(name='None')
    if maximum == result1:
        meilleur_traitement = [list_treatment[positions1[0][0]] , result1, [list_treatment[positions2[0][0]], result2, list_treatment[positions3[0][0]], result3]]
    if maximum == result2:
        meilleur_traitement = [list_treatment[positions2[0][0]] , result2, [list_treatment[positions1[0][0]], result1, list_treatment[positions3[0][0]], result3]]
    if maximum == result3:
        meilleur_traitement = [list_treatment[positions3[0][0]] , result3, [list_treatment[positions2[0][0]], result2, list_treatment[positions1[0][0]],result1]]


    return meilleur_traitement



### The third table is Admin for administrators

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, default='')
    password = db.Column(db.String(100), nullable=False, default='')
    is_superuser = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return '<Admin %r>' % self.username


###Functions associated with the admin page

@app.route("/admin")
def admin():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/login')
    else:
        patients = Patient.query.all()


        # Retrieve logged in admin username
        admin = session.get('admin_username')
    if request.method == 'POST':
            action = request.form.get('action')
            if action == 'register' and session.get('is_superuser'):
                return redirect('/admin/register')
            elif action == 'delete' and session.get('is_superuser'):
                admin_id = request.form.get('admin_id')
                admin = Admin.query.get(admin_id)
                if admin:
                    db.session.delete(admin)
                    db.session.commit()
                    flash('Admin delete ok')
                else:
                    flash('Admin not found')

    admins = Admin.query.all()
    treatments = TreatmentChemotherapy.query.all()
    print(treatments)
    return render_template('admin.html', patients=patients, admins=admins, admin=admin, treatments=treatments)

###To edit a patient in the database
@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    #Treatment creation if we need it
    treatment1 = TreatmentChemotherapy.query.filter_by(name='Capecitabin mono or 5-FU/FA').first()
    treatment2 = TreatmentChemotherapy.query.filter_by(name='Folfox 4 or Folfox 6 or Xelox').first()
    treatment3 = TreatmentChemotherapy.query.filter_by(name='Xelox + Bevacizumab or CapIri + Bevacizumab').first()
    treatment = TreatmentChemotherapy.query.filter_by(name='None').first()

    if not treatment1:
        treatment1 = TreatmentChemotherapy(name='Capecitabin mono or 5-FU/FA')
        db.session.add(treatment1)

    if not treatment2:
        treatment2 = TreatmentChemotherapy(name='Folfox 4 or Folfox 6 or Xelox')
        db.session.add(treatment2)

    if not treatment3:
        treatment3 = TreatmentChemotherapy(name='Xelox + Bevacizumab or CapIri + Bevacizumab')
        db.session.add(treatment3)

    if not treatment:
        treatment = TreatmentChemotherapy(name='None')
        db.session.add(treatment)

    db.session.commit()
    patient = Patient.query.get(id)
    treatments = TreatmentChemotherapy.query.all()
    if request.method == 'POST':
        #personal info
        patient.first_name = request.form['first_name']
        patient.last_name = request.form['last_name']
        patient.gender = request.form['gender']
        patient.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        patient.email = request.form['email']
        patient.weight = request.form['weight']
        patient.height = request.form['height']
        patient.op_date_primary_tumor = datetime.strptime(request.form['op_date_primary_tumor'], '%Y-%m-%d').date()
        patient.age_at_OP = request.form['age_at_OP']
        patient.BMI = request.form['BMI']
        #medical info
        patient.pre_existing_conditions = request.form['pre_existing_conditions']
        patient.cardiac_diseases = request.form['cardiac_diseases']
        patient.pulmonary_diseases = request.form['pulmonary_diseases']
        patient.urological_diseases = request.form['urological_diseases']
        patient.endocrine_diseases = request.form['endocrine_diseases']
        patient.previous_vascular_diseases = request.form['previous_vascular_diseases']
        #about the tumor
        patient.tumor_side = request.form['tumor_side']
        patient.tumor_marker_CEA = request.form['tumor_marker_CEA']
        patient.tumor_marker_CA19_9 = request.form['tumor_marker_CA19_9']
        patient.preoperative_endoscopy = request.form['preoperative_endoscopy']
        patient.surgical_procedure= request.form['surgical_procedure']
        patient.localization_OP= request.form['localization_OP']
        patient.T_stadium= request.form['T_stadium']
        patient.N_stadium= request.form['N_stadium']
        patient.UICC_Stadium= request.form['UICC_Stadium']
        patient.grading= request.form['grading']
        patient.lymphangiosis_carcinomatous= request.form['lymphangiosis_carcinomatous']
        patient.vascular_invasion= request.form['vascular_invasion']
        patient.perineural_invasion= request.form['perineural_invasion']
        patient.tumor_diameter_in_cm= request.form['tumor_diameter_in_cm']
        #treatment
        patient.progression_free_survival_in_months = request.form['progression_free_survival_in_months']

        # Retrieve the ID of the process selected in the form
        treatment_id = request.form.get('treatment')
        print(treatment_id)

        # Find the corresponding treatment in the database
        treatment = TreatmentChemotherapy.query.get(treatment_id)

        # Check if a treatment has been selected
        if treatment:
            # Delete all treatments previously associated with the patient
            patient.treatments.clear()
            # Add the new treatment to the patient
            patient.treatments.append(treatment)
        # Save changes to database


        db.session.commit()
        return redirect('/admin')

    return render_template('edit.html', patient=patient, treatments=treatments)

##Delete a patient
@app.route("/delete/<int:id>", methods=['POST', 'DELETE'])
def delete(id):
    patient = Patient.query.get(id)
    db.session.delete(patient)
    db.session.commit()
    return redirect('/admin')




# Route to display the login form


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            session['logged_in'] = True
            session['is_superuser'] = admin.is_superuser  # Stores the mode (superuser or normal)
            session['admin_username'] = admin.username
            return redirect('/admin')
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect('/admin')
        else:
            flash('Mauvais identifiant ou mot de passe')
    return render_template('login.html')


# Route to logout
@app.route("/logout", methods=['GET' , 'POST'])
def logout():
    session.pop('logged_in', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

##Create admin

@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    # Check if a superuser already exists or if there is no administrator
    if not has_admin() or session.get('is_superuser'):
        # Check if the form has been submitted
        if request.method == 'POST':
            # Retrieve data submitted in the form
            username = request.form['username']
            password = request.form['password']
            is_superuser = request.form.get('is_superuser') == 'on'
            # Create a new administrator
            admin = Admin(username=username, password=generate_password_hash(password), is_superuser=is_superuser)
            print(admin)

            #Add the new administrator to the database
            db.session.add(admin)
            db.session.commit()

            flash('Inscription réussie. Vous pouvez maintenant vous connecter en tant qu\'administrateur.')
            return redirect('/admin')

        # Show registration form
        return render_template('register.html', has_admin=has_admin)

    return render_template('error.html', has_admin=has_admin)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

##To delete an Admin
@app.route('/admin/delete/<int:id>', methods=['POST', 'DELETE'])
def admin_delete(id):
    if session.get('logged_in') and session.get('is_superuser'):
        if request.method == 'POST' or request.method == 'DELETE':
            admin = Admin.query.get(id)
            if admin.is_superuser:
                superusers_count = Admin.query.filter_by(is_superuser=True).count()
                if superusers_count <= 1:
                    flash('Suppression impossible. Il doit y avoir au moins un administrateur superutilisateur.')
                return redirect('/admin')
            db.session.delete(admin)
            db.session.commit()
            return redirect('/admin')
    else:
        flash('Accès non autorisé.')
        return redirect('/admin')


###Function only use during the programmation

## Create patient with an excel file




def create_patient_from_excel(file_path):
    treatment1 = TreatmentChemotherapy.query.filter_by(name='Capecitabin mono or 5-FU/FA').first()
    treatment2 = TreatmentChemotherapy.query.filter_by(name='Folfox 4 or Folfox 6 or Xelox').first()
    treatment3 = TreatmentChemotherapy.query.filter_by(name='Xelox + Bevacizumab or CapIri + Bevacizumab').first()
    treatment = TreatmentChemotherapy.query.filter_by(name='None').first()

    if not treatment1:
        treatment1 = TreatmentChemotherapy(name='Capecitabin mono or 5-FU/FA')
        db.session.add(treatment1)

    if not treatment2:
        treatment2 = TreatmentChemotherapy(name='Folfox 4 or Folfox 6 or Xelox')
        db.session.add(treatment2)

    if not treatment3:
        treatment3 = TreatmentChemotherapy(name='Xelox + Bevacizumab or CapIri + Bevacizumab')
        db.session.add(treatment3)

    if not treatment:
        treatment = TreatmentChemotherapy(name='None')
        db.session.add(treatment)

    db.session.commit()
    data = pd.read_excel(file_path, sheet_name=1)  # Specify the name or index of the second sheet (index 1)

    for _, row in data.iterrows():
        # Retrieve the values of the desired columns and create a Patient object
        first_name = row['Eingansbuchungsnummer']
        last_name = row['Eingansbuchungsnummer']
        gender = 'M' if row['Geschlecht'] == 1 else 'W'
        date_of_birth = row['Geburtsdatum']
        BMI = row['BMI_Einteilung']
        weight = row['Gewicht_in_kg']
        if pd.notnull(weight) and isinstance(weight, (int, float)):
            weight = float(weight)
        else:
            weight = None
        height = row['Größe_in_cm']
        if pd.notnull(height) and isinstance(height, (int, float)):
            height = float(height)
        else:
            height = None
        pre_existing_conditions = 'yes' if  row['Vorerkrankungen_vorhanden'] == 1 else 'no'
        op_date_primary_tumor = row['OP_Datum_Primärtumor']
        age_at_OP = row['Alter_bei_OP_1']
        cardiac_disease = 'no' if  row['kardiale_Vorerkrankungen'] == 0 else 'yes'
        pulmonary_diseases = 'yes' if  row['pulmonale_Vorerkrankung'] == 1 else 'no'
        urological_diseases = 'yes' if  row['urologische_Vorerkrankungen'] == 1 else 'no'
        endocrine_diseases = 'yes' if  row['endokrinologische_Vorerkrankung'] == 1 else 'no'
        previous_vascular_diseases = 'yes' if  row['vaskuläre_Vorerkrankungen'] == 1 else 'no'
        tumor_side = 'left' if  row['Tumorseite'] == 2 else 'right'
        tumor_marker_CEA = 'CEA in the normal range' if row['Tumormarker_CEA'] == 2 else ('CEA pathologic' if row['Tumormarker_CEA'] == 1 else 'CEA not determined')
        tumor_marker_CA19_9 = 'CA19_9 in the normal range' if row['Tumormarker_CA19_9'] == 2 else ('CA19_9 pathologic' if row['Tumormarker_CA19_9'] == 1 else 'CA19_9 not determined')
        preoperative_endoscopy = 'colonoscopy' if row['präoperative_Endoskopie'] == 1 else ('rectoscopy' if row['präoperative_Endoskopie'] == 2 else 'n/a')
        surgical_procedure = 'open surgery' if  row['Operationsverfahren'] == 1 else 'laparoscopy'
        localization_OP= 'left' if  row['Lokalisation_OP'] == 2 else 'right'

        T_stadium = ''
        if row['T_Stadium_gesamt'] == 1:
            T_stadium = 'pT1'
        elif row['T_Stadium_gesamt'] == 2:
            T_stadium = 'pT2'
        elif row['T_Stadium_gesamt'] == 3:
            T_stadium = 'pT3'
        else:
            T_stadium = 'pT4'


        N_stadium = ''
        if row['N_Stadium_gesamt'] == 1:
            N_stadium = 'pN0'
        elif row['N_Stadium_gesamt'] == 2:
            N_stadium = 'pN1'
        elif row['N_Stadium_gesamt'] == 3:
            N_stadium = 'pN2'
        else:
            N_stadium = ''


        UICC_stadium = ''
        if row['UICC_Stadium'] == 1:
            UICC_stadium = '1'
        elif row['UICC_Stadium'] == 2:
            UICC_stadium = '2a'
        elif row['UICC_Stadium'] == 3:
            UICC_stadium = '2b'
        elif row['UICC_Stadium'] == 4:
            UICC_stadium = '2c'
        elif row['UICC_Stadium'] == 5:
            UICC_stadium = '3a'
        elif row['UICC_Stadium'] == 6:
            UICC_stadium = '3b'
        elif row['UICC_Stadium'] == 7:
            UICC_stadium = '3c'
        else:
            UICC_stadium = ''

        grading= ''
        if row['Grading_gesamt'] == 1:
            grading= 'G1'
        elif row['Grading_gesamt'] == 2:
            grading= 'G2'
        elif row['Grading_gesamt'] == 3:
            grading= 'G3'
        elif row['Grading_gesamt'] == 4:
            grading= 'G4'
        else:
            grading= ''

        lymphangiosis_carcinomatous= ''
        if row['Lymphangiosis_carcinomatosa'] == 0:
            lymphangiosis_carcinomatous= 'L0'
        elif row['Lymphangiosis_carcinomatosa'] == 1:
            lymphangiosis_carcinomatous= 'L1'
        else:
            lymphangiosis_carcinomatous= 'n/a'

        vascular_invasion= ''
        if row['Gefäßinvasion'] == 0:
            vascular_invasion= 'V0'
        elif row['Gefäßinvasion'] == 1:
            vascular_invasion= 'V1'
        else:
            vascular_invasion= 'n/a'

        perineural_invasion= ''
        if row['Perineuralinvasion'] == 0:
            perineural_invasion= 'Pn0'
        elif row['Perineuralinvasion'] == 1:
            perineural_invasion= 'Pn1'
        else:
            perineural_invasion= 'n/a'


        tumor_diameter_in_cm= row['Tumordurchmesser_in_cm_1']

        progression_free_survival_in_months = row['Progressionsfreies_Überleben_in_Monaten']


        #Create the Patient object and save it to the database
        patient = Patient(first_name=first_name, last_name=last_name, gender=gender, date_of_birth=date_of_birth, BMI=BMI, weight=weight, height=height, pre_existing_conditions=pre_existing_conditions, op_date_primary_tumor=op_date_primary_tumor, age_at_OP=age_at_OP, cardiac_diseases=cardiac_disease, pulmonary_diseases=pulmonary_diseases, urological_diseases=urological_diseases, endocrine_diseases=endocrine_diseases,  previous_vascular_diseases=previous_vascular_diseases, tumor_side=tumor_side, tumor_marker_CEA=tumor_marker_CEA, tumor_marker_CA19_9=tumor_marker_CA19_9, preoperative_endoscopy=preoperative_endoscopy, surgical_procedure=surgical_procedure, localization_OP= localization_OP, T_stadium=T_stadium, N_stadium=N_stadium, UICC_Stadium=UICC_stadium, grading=grading,lymphangiosis_carcinomatous=lymphangiosis_carcinomatous, vascular_invasion=vascular_invasion, perineural_invasion=perineural_invasion, tumor_diameter_in_cm=tumor_diameter_in_cm, progression_free_survival_in_months = progression_free_survival_in_months   )

        treatment = None  # or another suitable default

        if row['Schema_1._Chemotherapie'] == 1:
            treatment = treatment1
            #patient.treatments.append(treatment1)

        elif row['Schema_1._Chemotherapie'] == 2:
            treatment = treatment2
            #patient.treatments.append(treatment2)
        elif row['Schema_1._Chemotherapie'] == 3:
            treatment = treatment3
            #patient.treatments.append(treatment3)
        else:
            print('None')

        db.session.add(patient)
        db.session.commit()
    return "Patients imported successfully"





@app.route('/import-patients')
def import_patients():
    create_patient_from_excel('data.xlsx')
    return 'Importation des patients terminée.'
if __name__ == '__main__':
    app.run()


##Delete all the patient from the database

@app.route('/admin/delete_all', methods=['POST'])
def delete_all_patients():
    try:
        # Delete all patients from the database
        Patient.query.delete()
        db.session.commit()
        message = 'All the patient are delete'
        return jsonify({'message': message})
    except Exception as e:
        # Handle any errors
        db.session.rollback()
        message = 'Error on the patients : {}'.format(str(e))
        return jsonify({'message': message}), 500


