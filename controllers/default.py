# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import Image
from gluon.serializers import json

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    projects = db().select(db.project.id, db.project.name,db.project.public)
    pubProjects = dict()
    unAuthProjects = dict()
    for project in projects:
        for row in db(db.project.public == True).select(db.project.id,db.project.name):
            pubProjects[project.id] = project.name
    authorizedProjects = dict()
    if auth.user_id == None:
        pass
    else :
        for project in projects:
            for row in db(db.authUsers.projectId == project.id).select():
                if project.public:
                    continue
                if row.user == auth.user_id:
                    authorizedProjects[project.id]=project.name
                    continue
                else:
                    unAuthProjects[project.id] = project.name
                    continue
    authorizedProjects = json(authorizedProjects)
    unAuthProjects = json(unAuthProjects)
    pubProjects = json(pubProjects)
    appName = json(request.application)
    return locals()

def createProject():
    if auth.user_id == None:
        form = SQLFORM(db.project, fields = ['name','width','height']).process()
    else :
        form = SQLFORM(db.project).process()
    if form.accepted:
        db.authUsers.insert(user=auth.user_id,
                            projectId=form.vars.id)
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
        redirect(URL("crop", args=form.vars.id))
    elif form.errors:
        session.flash=T('Unable to add image')
    else:
        pass
    return locals()

def crop():
    image = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    return dict(image = image.file)

def crop_image():
    import os
    import gluon.contenttype
    rec = db(db.image.id == request.vars.img).select().first()
    filename = rec.file
    response.headers['Content-Type']=gluon.contenttype.contenttype(filename)
    file_path=os.path.join(request.folder,'uploads/',filename)
    #print(URL('.../uploads'));
    #path = URL('.../uploads') + file_path
    print("1")
    fp = open(file_path, "rb")
    print("open")
    img = Image.open(fp)
    print("image")
    img.load()
    print("loads")
    box = (int(request.vars.x), int(request.vars.y), int(request.vars.x2), int(request.vars.y2))
    img = img.crop(box)
    fp.close()
    img.save(file_path)
    #newimg = Image.open(path)
    #projectId = rec.projectId
    #num = rec.num
    #version = rec.version
    #del db.image[request.vars.img]
    #db.image.insert(file=newimg, num=num, version=version, active=True, projectId=projectId)
    redirect(URL("show", vars=dict(projectId=rec.projectId, num=rec.num)), client_side=True)

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

#ajax callback for rearranging pictures
def updateNums():
    #if request.env.request_method!='POST': raise HTTP(400)
    args = request.post_vars.items()[0][1]
    projectId = int(args[0])
    swapFrom = int(args[1])
    swapTo = int(args[2])
    from_list = db((db.image.num == swapFrom) & (db.image.projectId == projectId)).select()
    to_list = db((db.image.num == swapTo) & (db.image.projectId == projectId)).select()
    for item in from_list:
        item.update_record(num=swapTo)
    for item in to_list:
        item.update_record(num=swapFrom)

#ajax callback for saving pictures
def saveImage():
    import os
    import gluon.contenttype
    import base64
    #if request.env.request_method!='POST': raise HTTP(400)
    args = request.post_vars.items()[0][1]
    projectId = int(args[0])
    num = int(args[1])
    data = args[2]
    title = args[3]
    oldImage = db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.active == True)).select().first()
    maxversion = db((db.image.num == num) & (db.image.projectId == projectId)).select(orderby=~db.image.version).first()
    if oldImage is None:
        version = 0;
    else:
        version=maxversion.version+1
        oldImage.update_record(active=False)
    filename = 'image.file.'+args[0]+'_'+args[1]+'_'+str(version)+'.png'
    response.headers['Content-Type']=gluon.contenttype.contenttype(filename)
    pathfilename=os.path.join(request.folder,'uploads/', filename)
    lhs, data = data.split(";", 1)
    lhs, data = data.split(",", 1)
    base64.b64decode(data)
    stream = open(pathfilename, 'wb')
    stream.write(data.decode('base64'))
    stream.close()
    db.image.insert(finished=False, num=num, title=title, active=True, version=version, file=filename, projectId=projectId)

def managePer():
    projId = request.vars['projId']
    project = db(db.project.id == projId).select().first()
    if project.created_by == None:
        session.flash = 'No owner to manage this project'
        redirect(URL("index"))
    elif project.created_by == auth.user_id:
        pass
    else:
        session.flash = 'Only the owner of this project can manage it'
        redirect(URL("index"))
    projectName = project.name
    form = SQLFORM(db.authUsers,fields=['user'])
    form.vars.projectId = projId
    form.process(onsuccess=lambda form: (

            auth.archive(form),
            form.record_id and
db(db.authUsers.id==form.record_id).update(projectId=projId)))
    if form.accepted:
        session.flash = 'Success'
    elif form.errors:
        session.flash = 'Unable to add user'
    authUsrs = SQLFORM.grid(query=(db.authUsers.projectId == projId), editable = False,csv=False,create=False)
    return locals()

def showSavedProject():
    projectId = request.vars['projectId']
    images = db((db.image.projectId == projectId) & (db.image.active == True)).select(db.image.ALL, orderby=db.image.num)
    project = db(db.project.id == projectId).select(db.project.ALL).first()
    index = 0
    project_im = Image.new('RGB', (project.width*100,project.height*100), "white")
    for i in xrange(0,project.width*100,100):
        for j in xrange(0,project.height*100,100):
            for image in images:
                if image.num == index:
                    im=Image.open(request.folder + 'uploads/' + image.file)
                    im.thumbnail((100,100))
                    project_im.paste(im, (j,i))
            index = index + 1
    projectImage='project.im.%s.png' % (project.name)
    projectImage = projectImage.replace(" ", "")
    project_im.save(request.folder + 'uploads/' + projectImage, 'png')
    project.update_record(im=projectImage)

    return locals()

def showImages():
    projectId = request.vars['projectId']
    images = db((db.image.projectId == projectId) & (db.image.active == True)).select(db.image.ALL, orderby=db.image.num)
    project = db(db.project.id == projectId).select(db.project.ALL).first()
    if project == None:
        session.flash = 'Project equals None'
        redirect(URL("index"))
    authorized = False
    if project.public :
        pass
    else:
        for row in db(db.authUsers.projectId == projectId).select():
            if row.user == auth.user_id:
                response.flash = 'You\'re in here'
                authorized = True
                break
        if authorized == False:
            session.flash = 'Not authorized to view this project'
            redirect(URL("index"))
    currUsrId = auth.user_id
    db.projectComment.projectId.default = project.id
    db.projectComment.projectId.readable = False
    db.projectComment.projectId.writeable = False
    form = SQLFORM(db.projectComment,fields = ['body']).process()
    comments = db(db.projectComment.projectId == project.id).select()
    return locals()

def show():
    projectId = request.vars['projectId']
    num = request.vars['num']
    project = db(db.project.id == projectId).select(db.project.ALL).first()
    if project == None:
        session.flash = 'Project equals None'
        redirect(URL("index"))
    authorized = False
    if project.public :
        pass
    else:
        for row in db(db.authUsers.projectId == projectId).select():
            if row.user == auth.user_id:
                response.flash = 'You\'re in here'
                authorized = True
                break
        if authorized == False:
            session.flash = 'Not authorized to view this project'
            redirect(URL("index"))
    image_list = db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.active == True))
    if image_list.isempty():
        image = None
        val = ''
    else:
        image = image_list.select().first()
        val = image.version
    versions_list = db((db.image.projectId == projectId) & (db.image.num == num)).select(db.image.ALL, orderby=db.image.version)
    itemstr = ''
    for item in versions_list:
        itemstr = itemstr + str(item.version)
        if item.title:
            itemstr = itemstr + '-' + item.title + ','
        else:
            itemstr = itemstr + ','
    #oldversions=FORM(SELECT(itemstr.split(',')),_name="oldversions", _onchange="version_change()")
    names = itemstr.split(',')
    form=FORM('Version:',
          SELECT(_name='version', _value=val,*[OPTION(names[i], _value=(i)) for i in range(len(versions_list))]),
          INPUT(_type='submit',_value='Revert'))
    if form.accepts(request,session):
        db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.active == True)).update(active=False);
        db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.version == form.vars.version)).update(active=True)
        image = db((db.image.num == num) & (db.image.projectId == projectId) & (db.image.active == True)).select().first()
    return dict(image=image, num=num, projectId=projectId, form=form)

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
