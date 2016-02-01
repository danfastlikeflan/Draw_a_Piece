from gluon.contrib.appconfig import AppConfig

myconf = AppConfig(reload=True)

db = DAL("sqlite://storage.sqlite", migrate=True)
## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')
from gluon.tools import Auth, Service, PluginManager


auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

# -*- coding: utf-8 -*-

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
#hello world


db.define_table('picture',
	Field('picture', type='upload'),
	Field('num','integer'),
	Field('finished','boolean'))

db.define_table('image',
   Field('finished','boolean',default=False),
   Field('num','integer'),
   Field('title', requires=IS_NOT_EMPTY()),
   Field('file', 'upload', requires=IS_NOT_EMPTY()))



db.define_table('project',
	Field('name', 'string'),
	Field('pictureId','reference picture'),
	Field('isPublic','boolean'),
	Field('width','integer'),
	Field('height','integer'))


db.define_table('userName',
	Field('name', 'string'),
	Field('projectId','reference project'))

db.image.num.writable = db.image.num.readable = False
db.project.pictureId.writable = db.project.pictureId.readable = False
db.userName.projectId.writable = db.userName.projectId.readable = False

db.project.pictureId.requires = IS_IN_DB(db, db.picture.id)
db.userName.projectId.requires = IS_IN_DB(db, db.project.id)
