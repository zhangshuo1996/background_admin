from flask import Blueprint, render_template, session, request
import json

from web_admin.blueprints.auth import login_required
from bson.objectid import ObjectId
from web_admin.service import teacher_info_service

#蓝图要注册，在utils/__init__.py中，from web_admin.blueprints.teacher_info import teacher_info_bp，在register_blueprints函数中注册
teacher_info_bp = Blueprint('teacher_info', __name__)

@teacher_info_bp.route('/teacher_info')
@login_required
def teacher_info():
    """
    将数据库中取出的关于待处理的教师修改信息发往前端
    :return: agent_feedback表中所有未处理的信息，honor和domain转换为字符串
    """
    modify_info = teacher_info_service.get_modify_info()

    return render_template('teacher_info.html',modify_info =modify_info)

@teacher_info_bp.route('/get_info_by_tid',methods=['POST'])
@login_required
def get_info_by_tid():
    """
    将处理中的教师的信息从basic_info表中，发往前端，以便于和商务提交的修改信息做对比
    :return: 该教师再basic_info表中的基本信息
    """
    teacher_id = request.form.get('teacher_id', type=int)
    #根据id从数据中获取教师信息
    teacher_info_from_db = teacher_info_service.get_info_from_db(teacher_id)
    return json.dumps(teacher_info_from_db,ensure_ascii=False)

@teacher_info_bp.route('/data_preservation', methods=['POST'])
@login_required
def data_preservation():
    """
    将商务提交的数据保存到数据库
    :return:
    """
    teacher_id = request.form.get('teacher_id')
    # 从前端得到的数据中得到的honor和domain从字符串转化为list
    honor_str= request.form.get('honor')
    if honor_str != '' and honor_str != None:
        honors = honor_str.split(' ')
    else:
        honors = []
    domain_str = request.form.get('domain')
    if domain_str != ''and domain_str != None:
        domain = domain_str.split(' ')
    else:
        #防止domain出现['']的情况
        domain = []
    obj_id = ObjectId(request.form.get('object_id'))
    if teacher_id == "None" or teacher_id == None or teacher_id == '':
    #处理新增数据
        data = {
            'name': request.form.get('name'),
            'school': request.form.get('school'),
            'institution': request.form.get('institution'),
            'department': request.form.get('department'),
            'birth_year': request.form.get('birth_year'),
            'title': request.form.get('title'),
            'honor': honors,
            'domain': domain,
            'email': request.form.get('email'),
            'office_number': request.form.get('office_number'),
            'phone_number': request.form.get('phone_number'),
            'edu_exp': request.form.get('edu_exp'),
            'id': teacher_id,
            'position': '',
            'patrnt_id': [],
            'funds_id': [],
            'paper_id': []
        }
        max_id = teacher_info_service.get_max_teacher_id()
        data['id'] = max_id+1
        try:
            teacher_info_service.insert_basic_info(data,obj_id)
            return json.dumps({"success": True, "message": "操作成功"})
        except:
            return json.dumps({"success": False, "message": "操作失败"})
    else:
    #处理修改数据
        data ={'name':request.form.get('name'),
                'school':request.form.get('school'),
                'institution':request.form.get('institution'),
               'department':request.form.get('department'),
                'birth_year':request.form.get('birth_year'),
                'title':request.form.get('title'),
                'honor':honors,
               'domain':domain,
                'email':request.form.get('email'),
                'office_number':request.form.get('office_number'),
                'phone_number':request.form.get('phone_number'),
                'edu_exp':request.form.get('edu_exp')}
        try:
            teacher_info_service.update_basic_info(teacher_id,obj_id,data)
            return json.dumps({"success": True, "message": "操作成功"})
        except:
            return json.dumps({"success": False, "message": "操作失败"})



@teacher_info_bp.route('/data_ignore', methods=['POST'])
@login_required
def data_ignore():
    """
    忽略商务提交的消息
    """
    obj_id = ObjectId(request.form.get('object_id'))
    try:
        teacher_info_service.update_status(obj_id)
        return json.dumps({"success": True, "message": "操作成功"})
    except Exception as e:
        print(e.args)


@teacher_info_bp.route('/teacher_search')
@login_required
def teacher_search():
    """
    跳转到教师搜索页面
    :return:
    """
    try:
        school = teacher_info_service.get_school()
        institution = teacher_info_service.get_institution(school[0])
        institution.append(" ")
        return render_template("teacher_search.html",school=school,institution=institution)
    except BaseException:
        return json.dumps({"success": False, "message": "发生错误，请稍后重试！"})

@teacher_info_bp.route("/get_institution",methods=["POST"])
@login_required
def get_institution():
    """
    获取所有学校名
    :return:
    """
    school = request.form.get("school")
    try:
        institution = teacher_info_service.get_institution(school)
        return json.dumps({"success": True,"institution":institution})
    except BaseException:
        return json.dumps({"success": False, "message": "操作失败"})

@teacher_info_bp.route("/get_teacher_info",methods=["POST"])
@login_required
def get_teacher_info():
    """
    根据学校名，学院名和教师名获取教师信息
    :return: teacher_info：教师名、学校名、学院名、头衔、出生年月、邮箱、办公电话、手机号码、教育经历
    """
    school = request.form.get("school")
    institution = request.form.get("institution")
    teacher = request.form.get("teacher")
    try:
        teacher_list = teacher_info_service.get_teacher_info(school,institution,teacher)
        if teacher_list is not None:
            teacher_info = {
                "name": teacher_list['name'],
                "university": teacher_list['school'],
                "college": teacher_list['institution'],
                "title": teacher_list['title'],
                "birthyear": teacher_list['birth_year'],
                "email": teacher_list['email'],
                "tel_num": teacher_list['office_number'],
                "phone_number": teacher_list['phone_number'],
                "edu_exp": teacher_list['edu_exp']
            }
            return json.dumps({"success": True, "teacher_info": teacher_info})
        else:
            return json.dumps({"success": False, "message": "没有此老师的信息"})
    except BaseException:
        return json.dumps({"success": False, "message": "没有此老师的信息"})