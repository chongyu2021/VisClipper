import json
from py2neo import Graph,Node,NodeMatcher,Relationship
try:
    with open('neo4j_cfg.json','r') as _cfg:
        _cfg=json.load(_cfg)
except:
    raise Exception('Need neo4j_cfg.json')
_graph = Graph(f"bolt://localhost:{_cfg['port']}", auth=(_cfg['username'], _cfg['password']))
_matcher = NodeMatcher(_graph)
def _create_materials_node(data):
    datas=data.copy()
    del datas['tag']
    material_node = _matcher.match("Material", **datas).first()
    if not material_node:
        properties = {key: value for key, value in data.items()}
        # 创建节点
        node = Node('Material', **properties)
        # 将节点添加到数据库中
        _graph.create(node)
        return node
    else:
        raise Exception(f'{datas} is already in the database')
def _get_tag_nodes(tag_names):
    if type(tag_names)!=list:
        tag_names=[tag_names]
    tag_nodes = []
    for tag_name in tag_names:
        # 检查数据库中是否存在具有指定名称的节点
        existing_tag_node = _matcher.match("tag", name=tag_name).first()
        # 如果不存在，创建节点并添加到列表中
        if not existing_tag_node:
            tag_node = Node("tag", name=tag_name)
            _graph.create(tag_node)
            tag_nodes.append(tag_node)
        else:
            tag_nodes.append(existing_tag_node)
    return tag_nodes
def _create_relations(tag_nodes,material_node):
    relation_ships=[]
    for tag_node in tag_nodes:
        relation_ships.append(Relationship(material_node,'belong',tag_node))
    for rel in relation_ships:
        _graph.create(rel)
    return relation_ships
_lis = ["tag", "name", "location", "start_frame", "end_frame", "description"]
#json_str输入json格式字符串
#json_path输入json文件路径
#kwargs输入以_lis中值为键值的字典，属性缺一不可
def Insert_materials(json_str=None,json_path=None,**kwargs):
    #获得字典
    if json_path:
        try:
            with open(json_path,'r') as jsfile:
                js=json.load(jsfile)
        except:
            raise Exception(f'Wrong path,con\'t find {json_path}')
    elif json_str:
        try:
            js = json.loads(json_str)
        except:
            raise Exception('unvalided json str')
    elif kwargs:
        js={}
        for i in _lis:
            try:
                js[i]=kwargs[i]
            except:
                raise Exception(f'need key "{i}"')
    #创建结点
    met_node=_create_materials_node(js)
    if js['tag']:
        tag_nodes=_get_tag_nodes(js['tag'])
        _create_relations(tag_nodes,met_node)

BELONG_ANYTAG='ANY'
BELONG_ALLTAG='ALL'
def find_materials_by_tag(tag_names,method):
    if type(tag_names)!=list:
        tag_names=[tag_names]
    # 构建 Cypher 查询字符串
    query = f"""
        MATCH (m:Material)
        WHERE {method}(tag_name IN $tag_names
                  WHERE (m)-[:belong]->(:tag {{name: tag_name}}))
        RETURN m
        """
    # 执行查询
    result = _graph.run(query, tag_names=tag_names)

    # 将结果转换为字典列表
    materials = [dict(record["m"]) for record in result]
    # 返回结果
    return materials
def all_materials():
    query = f"""
        MATCH (m:Material)
        RETURN m
        """
    # 执行查询
    result = _graph.run(query)
    # 将结果转换为字典列表
    materials = [dict(record["m"]) for record in result]
    # 返回结果
    return materials
def delete_all_nodes_and_relationships():
    # 构建 Cypher 查询字符串
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    # 执行查询
    _graph.run(query)

