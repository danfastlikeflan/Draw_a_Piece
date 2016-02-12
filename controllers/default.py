# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    projects = db().select(db.project.id, db.project.name)
    return dict(projects=projects)

def createProject():
    form = SQLFORM(db.project).process()
    if form.accepted:
        redirect(URL('showImages',vars=dict(projectId=form.vars.id)))
    elif form.errors:
        session.flash=T('Unable to create project')
    else:
        pass
    return locals()

def create():
    projectId = request.vars['projectId']
    num = request.vars['num']
    form = SQLFORM(db.image).process()
    image_list = db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.active == True))
    if image_list.isempty():
        version = 0;
    else:
        oldImage = image_list.select().first()
        version = oldImage.version;
        oldImage.update_record(version=version)
        oldImage.update_record(active=False)
        version = version + 1
    if form.accepted:
        rec = db(db.image.id==form.vars.id).select(db.image.ALL).first()
        rec.update_record(projectId=projectId)
        rec.update_record(num=num)
        rec.update_record(version=version)
        rec.update_record(active=True)
        redirect(URL("show", vars=dict(projectId=projectId, num=num)))
    elif form.errors:
        session.flash=T('Unable to add image')
    else:
        pass
    return locals()

def manage():
    grid = SQLFORM.grid(db.image)
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

def showImages():
    projectId = request.vars['projectId']
    images = db((db.image.projectId == projectId) & (db.image.active == True)).select(db.image.ALL, orderby=db.image.num)
    project = db(db.project.id == projectId).select(db.project.ALL).first()
    return dict(images=images, project=project)

def show():
    projectId = request.vars['projectId']
    num = request.vars['num']
    #image = db.image(db.image.num == imageNum and db.image.projectId == projectId)
    image_list = db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.active == True))
    if image_list.isempty():
        image = None
    else:
        image = image_list.select().first()
    return dict(image=image, num=num, projectId=projectId, count=image_list.count())

def getImage():
    projectId = request.vars['projectId']
    imageNum = request.vars['imageNum']
    #image = db.image(db.image.num == imageNum && db.project.id == projectId)
    image = db(db.image.num == imageNum).select(db.image.ALL).first()
    #image = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    return dict(image=image)

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
