from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user,current_user

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
bootstrap = Bootstrap(app)
app.config['SECRET_KEY']  = 'QfaM~xW.p2$z:koUAZ1h'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/projet_python'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db=SQLAlchemy(app)


@app.route('/test')
def test():
	print(app.config)
	return "<h1>Test</h1>"

@app.route('/')
def index():
	return redirect('/login')
#Proprietaire ==================================================
class Proprietaire(db.Model):
	__tablename__ = 'proprietaire'
	id = db.Column(db.Integer, primary_key=True) 
	numero = db.Column(db.String(50), nullable=False, unique=True)
	nom = db.Column(db.String(100), nullable=False)
	prenom = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	telephone = db.Column(db.String(100), nullable=False)
	adresse = db.Column(db.String(100), nullable=False)
	cni = db.Column(db.String(100), nullable=False)
	Foncier = db.relationship('Foncier', backref='proprietaire', lazy=True)
	typeProprietaire_id = db.Column(db.Integer, db.ForeignKey('typeProprietaire.id'),
	nullable=False)

	def __repr__(self):
		return '<Proprietaire %r>' % self.nom

#Notaire ==================================================
class Notaire(db.Model):
	__tablename__ = 'notaire'
	id = db.Column(db.Integer, primary_key=True) 
	numero = db.Column(db.String(50), nullable=False, unique=True)
	nom = db.Column(db.String(100), nullable=False)
	prenom = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	telephone = db.Column(db.String(100), nullable=False)
	adresse = db.Column(db.String(100), nullable=False)
	cni = db.Column(db.String(100), nullable=False)
	Foncier = db.relationship('Foncier', backref='notaire', lazy=True)

	def __repr__(self):
		return '<Notaire %r>' % self.nom


#User ===================================================================
class User(UserMixin,db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	nom = db.Column(db.String(100), nullable=False)
	prenom = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	telephone = db.Column(db.String(100), nullable=False)
	adresse = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(100), nullable=False)
	#Foncier = db.relationship('Foncier', backref='user', lazy=True)

	def __repr__(self):
		return '<User %r>' % self.nom


#Terrain ======================================================================
class Terrain(db.Model):
	__tablename__ = 'terrain'
	id = db.Column(db.Integer, primary_key=True)
	numero = db.Column(db.String(100), nullable=False, unique=True)
	superfice = db.Column(db.Float, nullable=False)
	longitude = db.Column(db.String(100), nullable=False)
	latitude = db.Column(db.String(100), nullable=False)
	foncier = db.relationship("Foncier", uselist=False, backref="terrain")
	vente = db.relationship("Vente", uselist=False, backref="terrain")

	def __repr__(self):
		return '<Terrain %r>' % self.numero

#Type ======================================================================
class TypeProprietaire(db.Model):
	__tablename__ = 'typeProprietaire'
	id = db.Column(db.Integer, primary_key=True)
	libelle = db.Column(db.String(100), nullable=False, unique=True)
	proprietaire = db.relationship("Proprietaire", uselist=False, backref="typeProprietaire")

	def __repr__(self):
		return '<TypeProprietaire %r>' % self.libelle


#Foncier =========================================================================
class Foncier(db.Model):
	__tablename__ = 'foncier'
	id = db.Column(db.Integer, primary_key=True)
	numero = db.Column(db.String(50), nullable=False, unique=True)
	proprietaire_id = db.Column(db.Integer, db.ForeignKey('proprietaire.id'),
	nullable=False)
	notaire_id = db.Column(db.Integer, db.ForeignKey('notaire.id'),
	nullable=False)
	#user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
	#nullable=False)
	terrain_id = db.Column(db.Integer, db.ForeignKey('terrain.id'),
	nullable=False)
 
 #Vente =========================================================================
class Vente(db.Model):
	__tablename__ = 'vente'
	id = db.Column(db.Integer, primary_key=True)
	numero = db.Column(db.String(50), nullable=False, unique=True)
	montant = db.Column(db.String(50), nullable=False, unique=False)
	acheteur_id = db.Column(db.Integer, db.ForeignKey('proprietaire.id'),
	nullable=False)
	vendeur_id = db.Column(db.Integer, db.ForeignKey('proprietaire.id'),
	nullable=False)
	terrain_id = db.Column(db.Integer, db.ForeignKey('terrain.id'),
	nullable=False)

#====================================================================

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':     
		user = User.query.filter_by(email=request.form['email']).first()

		if user is not None and user.password == request.form['password']:
			return redirect('/accueil')
		#flash('Invalid username or password.')
		error = 'Email ou Password non valide'
  
	return render_template('/home/login.html',error=error)


@app.route('/logout')
def logout():
	return redirect('/login')

@app.route('/accueil')
def accueil():
	#logout_user()
	return render_template('/home/accueil.html')
#=========================================
@app.route('/foncier/add', methods=['GET', 'POST'])
def foncier_Add():
	last_foncier = db.session.query(Foncier).order_by(Foncier.id.desc()).first()
	idMax = 0
	if last_foncier is None:
		idMax = 1
	else:
		idMax = last_foncier.id +1
  
	numero = "F-00{}"
	numero = numero.format(idMax)
	#Recupération des acheteur et vendeur
	data_proprietaire = {}
	data_notaire = {}
	data_terrain = {}
	data_foncier = {}
	data_proprietaire = Proprietaire.query.all()
	data_notaire = Notaire.query.all()
	data_terrain = Terrain.query.all()
	data_foncier = db.session.query(Foncier, Proprietaire).join(Foncier, Foncier.proprietaire_id == Proprietaire.id).add_columns(Foncier.numero,Proprietaire.nom,Proprietaire.prenom).all() 
	
	if request.method == 'POST': 
		foncier = Foncier()
		foncier.numero = request.form['numero']
		foncier.proprietaire_id = request.form['proprietaire']
		foncier.notaire_id = request.form['notaire']
		foncier.terrain_id = request.form['terrain']
		
		db.session.add(foncier)
		try:
			db.session.commit()
			#succes = 'Proprietaire ajouter avec succés'
			flash('Titre Foncier ajouter avec succés')
			return redirect(url_for('foncier_Add'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
	return render_template('/foncier/add.html', numero=numero,data_proprietaire=data_proprietaire,data_notaire=data_notaire,data_terrain=data_terrain, data_foncier=data_foncier )

@app.route('/foncier/list')
def foncier_list():
	data_foncier = db.session.query(Foncier, Proprietaire).join(Foncier, Foncier.proprietaire_id == Proprietaire.id).\
	add_columns(Foncier.id, Foncier.numero, Proprietaire.nom, Proprietaire.prenom).all()
	return render_template('/foncier/list.html', data_foncier = data_foncier)

@app.route('/foncier/update/<id>', methods=['GET','POST'])
def foncier_update(id):
	data_proprietaire = Proprietaire.query.all()
	data_notaire = Notaire.query.all()
	Foncier_terrain = db.session.query(Foncier, Terrain).join(Foncier, Foncier.terrain_id == Terrain.id).\
	add_columns(Terrain.numero).filter_by(id=id)
	data_num = db.session.query(Foncier, Notaire).join(Foncier, Foncier.notaire_id == Notaire.id).\
	add_columns(Foncier.id, Foncier.numero, Notaire.nom, Notaire.prenom).filter_by(id=id)
 
	if request.method == 'POST':
		foncier = Foncier.query.filter_by(numero=request.form['numero']).first()
		foncier.proprietaire_id = request.form['proprietaire']
		foncier.notaire_id = request.form['notaire']
		
		try:
			db.session.commit()
			#succes = 'Proprietaire ajouter avec succés'
			flash('Titre Foncier modifier avec succés')
			return redirect(url_for('foncier_list'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
	return render_template('/foncier/updateFoncier.html', Foncier_terrain=Foncier_terrain,data_num=data_num, data_proprietaire=data_proprietaire, data_notaire=data_notaire)

@app.route('/foncier/pdf/<id>', methods=['GET', 'POST'])
def pdfGenered(id):
	data = db.session.query(Foncier, Terrain).join(Foncier, Foncier.terrain_id == Terrain.id).\
	add_columns(Terrain.numero).filter_by(id=id)  	
	prop = db.session.query(Foncier, Proprietaire).join(Foncier, Foncier.proprietaire_id == Proprietaire.id).\
	add_columns(Proprietaire.nom, Proprietaire.prenom).filter_by(id=id)
	html = render_template('foncier/pdf.html', data=data, prop=prop)
	return render_pdf(HTML(string=html))
#===========================================
@app.route('/notaire/add', methods=['GET', 'POST'])
def notaire_add():
	
	last_not = db.session.query(Notaire).order_by(Notaire.id.desc()).first()
	idMax = 0
	if last_not is None:
		idMax = 1
	else:
		idMax = last_not.id +1
  
	numero = "NT-00{}"
	numero = numero.format(idMax)
	#lister notaire
	data = {}
	data = Notaire.query.all()
 
	if request.method == 'POST': 
		notaire = Notaire()
		notaire.numero = request.form['numero']
		notaire.nom = request.form['nom']
		notaire.prenom = request.form['prenom']
		notaire.adresse = request.form['adresse']
		notaire.email = request.form['email']
		notaire.cni = request.form['cni']
		notaire.telephone = request.form['telephone']
  
		db.session.add(notaire)
		try:
			db.session.commit()
			flash('Notaire ajouter avec succés')
			return redirect(url_for('notaire_add'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
   
	return render_template('/notaire/add.html', data=data, numero=numero)

@app.route('/notaire/list')
def notaire_list():
	data = {}
	data = Notaire.query.all()
 
	return render_template('/notaire/list.html', data=data)

@app.route('/notaire/update/<id>', methods=['GET', 'POST'])
def notaire_update(id):
	notaire = Notaire.query.filter_by(id=id).first()
	data = {}
	data = Notaire.query.all()
 
	if request.method == 'POST':
		notaire = Notaire.query.filter_by(id=id).first()
		notaire.nom = request.form['nom']
		notaire.prenom = request.form['prenom']
		notaire.adresse = request.form['adresse']
		notaire.email = request.form['email']
		notaire.cni = request.form['cni']
		notaire.telephone = request.form['telephone']
		try:
			db.session.commit()
			flash('Notaire modifier avec succés')
			return redirect(url_for('notaire_list'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
	return render_template('/notaire/update_not.html', notaire=notaire, data=data)

@app.route('/notaire/delete/<id>', methods=['GET', 'POST'])
def notaire_delete(id):
	notaire = Notaire.query.filter_by(id=id).first()
	try:
		db.session.delete(notaire)
		db.session.commit()
		flash('Notaire supprimé avec succés')
	except Exception:
		print('Des erreurs sont survenues lors de la persistance des données')
		
	data = {}
	data = Notaire.query.all()
	return render_template('/notaire/list.html', data=data)
#================================================
@app.route('/proprietaire/add', methods=['GET', 'POST'])
def prop_add():
	last_prop = db.session.query(Proprietaire).order_by(Proprietaire.id.desc()).first()
	idMax = 0
	if last_prop is None:
		idMax = 1
	else:
		idMax = last_prop.id +1
  
	numero = "PP-00{}"
	numero = numero.format(idMax)
	#lister proprietaire
	data = {}
	data = Proprietaire.query.all()
 
	if request.method == 'POST': 
		prop = Proprietaire()
		prop.numero = request.form['numero']
		prop.nom = request.form['nom']
		prop.prenom = request.form['prenom']
		prop.adresse = request.form['adresse']
		prop.email = request.form['email']
		prop.cni = request.form['cni']
		prop.telephone = request.form['telephone']
		#prop.typeProprietaire_id = 1
  
		if request.form['type'] == 'Acheteur':
			  prop.typeProprietaire_id = 1
		else:
			prop.typeProprietaire_id = 2
		db.session.add(prop)
		try:
			db.session.commit()
			#succes = 'Proprietaire ajouter avec succés'
			flash('Proprietaire ajouter avec succés')
			return redirect(url_for('prop_add'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')

	return render_template('/proprietaire/add.html', numero=numero, data=data)

@app.route('/proprietaire/list')
def prop_list():
	data = {}
	data = Proprietaire.query.all()
	return render_template('/proprietaire/list.html',data=data)

@app.route('/proprietaire/update/<id>', methods=['GET', 'POST'])
def prop_update(id):
	#lister proprietaire
	prop = Proprietaire.query.filter_by(id=id).first()
	data = {}
	data = Proprietaire.query.all()
 
	if request.method == 'POST': 
		prop = Proprietaire.query.filter_by(id=id).first()
		prop.nom = request.form['nom']
		prop.prenom = request.form['prenom']
		prop.adresse = request.form['adresse']
		prop.email = request.form['email']
		prop.cni = request.form['cni']
		prop.telephone = request.form['telephone']
		#prop.typeProprietaire_id = 1
  
		if request.form['type'] == 'Acheteur':
			prop.typeProprietaire_id = 1
		else:
			prop.typeProprietaire_id = 2
		
		try:
			db.session.commit()
			#succes = 'Proprietaire ajouter avec succés'
			flash('Proprietaire Modifier avec succés')
			return redirect(url_for('prop_list'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
	return render_template('/proprietaire/update_Prop.html',prop=prop, data=data)

@app.route('/proprietaire/delete/<id>')
def prop_delete(id):
	data = {}
	data = Proprietaire.query.all()
	prop = Proprietaire.query.filter_by(id=id).first()
	try:
		db.session.delete(prop)
		db.session.commit()
		flash('Proprietaire supprimé avec succés')
	except Exception:
		print('Des erreurs sont survenues lors de la persistance des données')
	data = {}
	data = Proprietaire.query.all()
	return render_template('/proprietaire/list.html',data=data)

#===========================================
@app.route('/vente/add', methods=['GET', 'POST'])
def vente_add():
	last_vente = db.session.query(Vente).order_by(Vente.id.desc()).first()
	idMax = 0
	if last_vente is None:
		idMax = 1
	else:
		idMax = last_vente.id +1
  
	numero = "V-00{}"
	numero = numero.format(idMax)
	#Recupération des acheteur et vendeur
	data_acheteur = {}
	data_vendeur = {}
	data_terrain = {}
	data_vente = {}
	data_acheteur = Proprietaire.query.filter_by(typeProprietaire_id=1)
	data_vendeur = Proprietaire.query.filter_by(typeProprietaire_id=2)
	data_terrain = Terrain.query.all()
	data_vente = Vente.query.all()
 
	if request.method == 'POST': 
		vente = Vente()
		vente.numero = request.form['numero']
		vente.montant = request.form['montant']
		vente.acheteur_id = request.form['acheteur']
		vente.vendeur_id = request.form['vendeur']
		vente.terrain_id = request.form['terrain']
		
		db.session.add(vente)
		try:
			db.session.commit()
			#succes = 'Proprietaire ajouter avec succés'
			flash('Vente ajouter avec succés')
			return redirect(url_for('vente_add'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
	return render_template('/vente/add.html', numero=numero, data_acheteur=data_acheteur, data_vendeur=data_vendeur, data_terrain=data_terrain,data_vente=data_vente)

@app.route('/vente/list')
def vente_list():
	data_vente = db.session.query(Vente, Terrain).join(Vente, Vente.terrain_id == Terrain.id).\
	add_columns(Vente.numero,Vente.montant,Terrain.numero).all()
	return render_template('/vente/list.html', data_vente=data_vente)

#================================================
@app.route('/terrain/add', methods=['GET', 'POST'])
def terrain_add():
	last_terrain = db.session.query(Terrain).order_by(Terrain.id.desc()).first()
	idMax = 0
	if last_terrain is None:
		idMax = 1
	else:
		idMax = last_terrain.id +1
  
	numero = "T-00{}"
	numero = numero.format(idMax)
	
	data = {}
	data = Terrain.query.all()
 
	if request.method == 'POST': 
		terrain = Terrain()
		terrain.numero = request.form['numero']
		terrain.superfice = request.form['superficie']
		terrain.latitude = request.form['latitude']
		terrain.longitude = request.form['longitude']
		
  
		db.session.add(terrain)
  
		try:
			db.session.commit()
			#succes = 'Proprietaire ajouter avec succés'
			flash('Terrain ajouter avec succés')
			return redirect(url_for('terrain_add'))
		except Exception:
			print('Des erreurs sont survenues lors de la persistance des données')
	return render_template('/terrain/add.html', numero=numero, data=data)

@app.route('/terrain/list')
def terrain_list():
	data = {}
	data = Terrain.query.all()
	return render_template('/terrain/list.html', data=data)

if __name__ == '__main__': 
	app.run(debug=True,host='0.0.0.0', port='24000')