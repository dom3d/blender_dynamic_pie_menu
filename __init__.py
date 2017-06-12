import bpy
from bpy.types import Menu

# this is not writting the pythonic way

# http://programtalk.com/vs2/python/9063/coa_tools/Blender/coa_tools/operators/pie_menu.py/
# spawn an edit mode selection pie (run while object is in edit mode to get a valid output)

bl_info = {
    "name": "Dom's Dynamic Spacebar Pie",
    "author": "Dom",
    "version": (0, 0, 1),
    "blender": (2, 72, 0),
    "location": "View3D > Spacebar Key",
    "description": "Context Sensitive Pie Variations",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
    "Scripts/3D_interaction/Dynamic_Spacebar_Menu",
    "tracker_url": "",
    "category": "3D View"}

# contains code taken from all over the place (open source scripts that is)

############################
# Helpers

# icon method used from: http://blenderscripting.blogspot.ie/2015/06/blende-pie-menu-with-custom-icons.html
def DomPie_LoadIcons():
    import os
    import glob
    import bpy.utils.previews
    if 'icon_groups' in globals():
        DomPie_UnloadIcons()
    print(">> Loading Dom's Icons")
    global dompie_icons
    dompie_icons  = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    glob_token = os.path.join(icons_dir, "*.png")
    #print("searching :" + glob_token)
    for filename in glob.glob(glob_token):
        #print("Found file: " + filename)
        img_path = os.path.join(icons_dir, filename)
        img_base = os.path.basename(img_path)
        img_name = os.path.splitext(img_base)[0]
        dompie_icons.load(img_name, img_path, 'IMAGE')

def DomPie_UnloadIcons():
    if dompie_icons is None:
        return
    bpy.utils.previews.remove(dompie_icons)

def DomPie_isThemeDark():
    # tring to figure out if the used them is light or dark
    current_theme_name = bpy.context.user_preferences.themes.items()[0][0]
    current_theme = bpy.context.user_preferences.themes[current_theme_name]
    color = current_theme.user_interface.wcol_tool.inner
    grey = (color[0] + color[1] + color[2]) / 3.0
    return grey < 0.5
    
def DomPie_IconID(name, active):
    # todo fallback to standard icon if not found
    is_dark = DomPie_isThemeDark()
    if (is_dark and active) or (not is_dark and not active):
        dark = name + "_dark"
        if dark in dompie_icons:
            name = dark
    return dompie_icons[name].icon_id

# direct switcher code by Cedric L.
# faster mode mentioned here, something to look into:
# http://blender.stackexchange.com/questions/7064/switch-to-vertex-edge-face-mode-in-edit-mode-via-python
# if not bpy.context.object.mode == 'EDIT':
# bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
# bpy.context.scene.tool_settings.mesh_select_mode = (True, False, False)
# the slow version is:
#col.operator("mesh.select_mode", text=" ", icon='VERTEXSEL').type = 'VERT'
#col.operator("mesh.select_mode", text=" ", icon='EDGESEL').type = 'EDGE'
#col.operator("mesh.select_mode", text=" ", icon='FACESEL').type = 'FACE'

class InstantVertexMode(bpy.types.Operator):
    bl_idname = "domops.govertex"
    bl_label = "Vertex Mode"
    def execute(self, context):
        layout = self.layout
        if bpy.context.object.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        if bpy.ops.mesh.select_mode != "EDGE, FACE":
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
        return {'FINISHED'}

class InstantEdgeMode(bpy.types.Operator):
    bl_idname = "domops.goedge"
    bl_label = "Edge Mode"
    def execute(self, context):
        layout = self.layout
        if bpy.context.object.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        if bpy.ops.mesh.select_mode != "VERT, FACE":
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        return {'FINISHED'}

class InstantFaceMode(bpy.types.Operator):
    bl_idname = "domops.goface"
    bl_label = "Face Mode"    
    def execute(self, context):
        layout = self.layout
        if bpy.context.object.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        if bpy.ops.mesh.select_mode != "VERT, EDGE":
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')            
        return {'FINISHED'}


#############################
# Pie Delete - X
def DomPie_Test(pie, context):
    #4 - LEFT
    pie.operator("mesh.delete", text="Delete Vertices", icon='VERTEXSEL').type='VERT'
    #6 - RIGHT
    pie.operator("mesh.delete", text="Delete Faces", icon='FACESEL').type='FACE'
    #2 - BOTTOM
    pie.operator("mesh.delete", text="Delete Edges", icon='EDGESEL').type='EDGE'
    #8 - TOP
    pie.operator("mesh.dissolve_edges", text="Dissolve Edges", icon='SNAP_EDGE')
    #7 - TOP - LEFT
    pie.operator("mesh.dissolve_verts", text="Dissolve Vertices", icon='SNAP_VERTEX')
    #9 - TOP - RIGHT
    pie.operator("mesh.dissolve_faces", text="Dissolve Faces", icon='SNAP_FACE')
    #1 - BOTTOM - LEFT
    box = pie.split().column()
    row = box.row(align=True)
    box.operator("delete.limiteddissolve", text="Limited Dissolve", icon= 'STICKY_UVS_LOC')
    box.operator("mesh.delete_edgeloop", text="Delete Edge Loops", icon='BORDER_LASSO')
    box.operator("mesh.edge_collapse", text="Edge Collapse", icon='UV_EDGESEL')
    #3 - BOTTOM - RIGHT
    box = pie.split().column()
    row = box.row(align=True)
    box.operator("mesh.delete", text="Only Edge & Faces", icon='SPACE2').type='EDGE_FACE'
    box.operator("mesh.delete", text="Only Faces", icon='UV_FACESEL').type='ONLY_FACE'

def DomPie_ShelfAndProps(pie, context):
    split = pie.split()
    group01 = split.column (align=True)
    row01 = group01.row(align=True)
    row01.menu("VIEW3D_MT_view", text=" ", icon_value = DomPie_IconID("view", False))
    row01.menu("VIEW3D_MT_view_cameras", text=" ", icon_value = DomPie_IconID("camera", False))
    row02 = group01.row(align=True)
    row02.operator("view3d.toolshelf", text=" ", icon_value = DomPie_IconID("toolshelf", False))
    row02.operator("view3d.properties", text=" ", icon_value = DomPie_IconID("properties", False))


def DomPie_ManipulatorBox(pie, context):
    split = pie.split()
    group01 = split.column (align=True)
    row01 = group01.row(align=True)
    """
    op_props = col.operator("wm.context_set_enum", text="Local", icon='NONE')
    op_props.data_path = "space_data.transform_orientation"
    op_props.value = 'LOCAL'
    op_props = col.operator("wm.context_set_enum", text="Global", icon='NONE')
    op_props.data_path = "space_data.transform_orientation"
    op_props.value = 'GLOBAL'
    op_props = col.operator("wm.context_set_enum", text="Normal", icon='NONE')
    op_props.data_path = "space_data.transform_orientation"
    op_props.value = 'NORMAL'
    op_props = col.operator("wm.context_set_enum", text="View", icon='NONE')
    op_props.data_path = "space_data.transform_orientation"
    op_props.value = 'VIEW'
    op_props = col.operator("wm.context_set_enum", text="Gimbal", icon='NONE')
    op_props.data_path = "space_data.transform_orientation"
    op_props.value = 'GIMBAL'
    """
    # transformation manipulators  
    #prop = row01.operator("view3d.enable_manipulator", text=' ', icon_value=dompie_icons["translate2"].icon_id, emboss = (bpy.context.space_data.transform_manipulators != {'TRANSLATE'}))
    active = bpy.context.space_data.transform_manipulators == {'TRANSLATE'}
    prop = row01.operator("view3d.enable_manipulator", text=' ', icon_value = DomPie_IconID("translate", active))
    prop.translate = True
    active = bpy.context.space_data.transform_manipulators == {'ROTATE'}
    prop = row01.operator("view3d.enable_manipulator", text=' ', icon_value = DomPie_IconID("rotate", active))
    prop.rotate = True
    active = bpy.context.space_data.transform_manipulators == {'SCALE'}
    prop = row01.operator("view3d.enable_manipulator", text=' ', icon_value = DomPie_IconID("scale", active))
    prop.scale = True
    active = bpy.context.space_data.transform_manipulators == {'TRANSLATE', 'ROTATE', 'SCALE'}
    prop = row01.operator("view3d.enable_manipulator", text=' ', icon_value = DomPie_IconID("universal", active))
    prop.scale = True
    prop.rotate = True
    prop.translate = True
    active = bpy.context.space_data.transform_manipulators == {}
    prop = row01.operator("view3d.enable_manipulator", text=' ', icon_value = DomPie_IconID("disallow", active))
    prop.scale = False
    prop.rotate = False
    prop.translate = False
    # transformation space dropdown selector
    row02 = group01.row(align=True)
    row02.prop(context.space_data, "transform_orientation", text="")
    #pivot
    row03 = group01.row(align=True)
    row03.operator_menu_enum("object.origin_set", "type")


def DomPie_MeshEditModes(pie, context):
    split = pie.split()
    #box = split.box() # we can use this if we want a boxed background
    grp01 = split.column(align=True)
    row01 = grp01.row(align=True)

    # display object or edit mode-icon
    if context.edit_object:
        row01.operator("object.mode_set", text=" ", icon='OBJECT_DATAMODE').mode = 'OBJECT'
    else:
        row01.operator("object.mode_set", text=" ", icon='EDITMODE_HLT').mode = 'EDIT'

    # includes on / off states for mesh selection modes
    select_modes = list(bpy.context.scene.tool_settings.mesh_select_mode)
    current_mode_idx = select_modes.index(True)
    if not context.edit_object:
        current_mode_idx = -1
    row01.operator("domops.govertex", text=" ", icon='VERTEXSEL', emboss = (current_mode_idx is not 0))
    row01.operator("domops.goedge", text=" ", icon='EDGESEL', emboss = (current_mode_idx is not 1))
    row01.operator("domops.goface", text=" ", icon='FACESEL', emboss = (current_mode_idx is not 2))

    row02 = grp01.row(align=True)
    prop = row02.operator("wm.context_set_value", text=" ", icon='EDITMODE_HLT')
    prop.value = "(True, True, False)"
    prop.data_path = "tool_settings.mesh_select_mode"

    prop = row02.operator("wm.context_set_value", text=" ", icon='ORTHO')
    prop.value = "(True, False, True)"
    prop.data_path = "tool_settings.mesh_select_mode"

    prop = row02.operator("wm.context_set_value", text=" ", icon='SNAP_FACE')
    prop.value = "(False, True, True)"
    prop.data_path = "tool_settings.mesh_select_mode"

    prop = row02.operator("wm.context_set_value", text=" ", icon='SNAP_VOLUME')
    prop.value = "(True, True, True)"
    prop.data_path = "tool_settings.mesh_select_mode"
 
def DomPie_SelectAddDelete(pie, context):
    split = pie.split()
    group01 = split.column (align=True)
    # add
    row01 = group01.row(align=True)
    row01.operator("wm.call_menu", text="Add Object", icon='MENU_PANEL').name="INFO_MT_add"
    row01.operator_menu_enum("object.modifier_add", "type", icon='MODIFIER')
    # select
    row02 = group01.row(align=True)
    if context.mode == 'OBJECT':
        row02.operator("wm.call_menu", text="Select", icon='MENU_PANEL').name="VIEW3D_MT_select_object"
    elif context.mode == "EDIT_MESH":
        row02.operator("wm.call_menu", text="Select", icon='MENU_PANEL').name="VIEW3D_MT_select_edit_mesh"
    
def DomPie_EditMeshCommonSelectionOps(pie, context):
    split = pie.split()
    group01 = split.column (align=True)
    row01 = group01.row(align=True)
    
    select_modes = list(bpy.context.scene.tool_settings.mesh_select_mode)
    current_mode_idx = select_modes.index(True)
    if not context.edit_object:
        return
    # 0 = verts, 1 edge, 2 faces
    # current_mode_idx is not 0

    if current_mode_idx is 0:
        # verts
        row01.operator("mesh.select_shortest_path", text="Path")

    elif current_mode_idx is 1:
        # edge
        row01.operator("mesh.loop_multi_select", text="Loop")
        row01.operator("mesh.loop_multi_select", text="Ring").ring = True
        #row01.operator("mesh.select_next_loop", text="Next Loop")
        #row01.operator("mesh.select_shortest_path", text="Path")
        row02 = group01.row(align=True)
        row02.operator("mesh.select_all", text="All")
        row02.operator("mesh.select_less", text="Less")
        row02.operator("mesh.select_more", text="More").use_face_step = False
    elif current_mode_idx is 2:
        row02 = group01.row(align=True)
        row02.operator("mesh.select_all", text="All")
        row02.operator("mesh.select_less", text="Less")
        row02.operator("mesh.select_more", text="More").use_face_step = True


 
def DomPie_EditMeshCommonEditOps(pie, context):
    split = pie.split()
    group01 = split.column (align=True)
    row01 = group01.row(align=True)    
    print(context.mode)
    select_modes = list(bpy.context.scene.tool_settings.mesh_select_mode)
    current_mode_idx = select_modes.index(True)
    if not context.edit_object:
        return
    if current_mode_idx is 0:
        # verts ----------------------------------------------------------
        row01.operator("mesh.connect", text="Connect")
        row01.operator("mesh.smooth", text="Smooth")
        row03 = group01.row(align=True)
        row03.operator("mesh.extrude_vertices_move", text="Extrude")
        row03.operator("mesh.extrude_edges_indiv", text="Indv")
        row03.operator("mesh.extrude_region", text="Region")
    if current_mode_idx is 1:
        # edges ----------------------------------------------------------
        row01.operator("mesh.loopcut_slide", text="Cut Slide Loop")
        row01.operator("mesh.knife_tool", text="Knife")
        row01.operator("mesh.subdivide", text="Subdivide")
        row02 = group01.row(align=True)
        row02.operator("mesh.bevel", text="Bevel")
        row02.operator("mesh.bridge_edge_loops", text="Loop Bridge")
        row02.operator("mesh.solidify", text="Solidify")
        row03 = group01.row(align=True)
        row03.operator("mesh.extrude_edges_move", text="Extrude")
        row03.operator("mesh.extrude_edges_indiv", text="Indv")
        row03.operator("mesh.extrude_region", text="Region")
        row03.operator("mesh.dupli_extrude_cursor", text="Cursor")
        row04 = group01.row(align=True)
        row04.operator("mesh.edge_face_add", text="Add")
        row04.operator("mesh.fill", text="Fill")
    if current_mode_idx is 2:
        # faces ----------------------------------------------------------
        row01.operator("mesh.loopcut_slide", text="Cut Slide Loop")
        row01.operator("mesh.knife_tool", text="Knife")
        row01.operator("mesh.subdivide", text="Subdivide")
        row02 = group01.row(align=True)
        #row01.operator("mesh.edge_face_add", text="Add")
        row02.operator("mesh.inset", text="Inset")
        row02.operator("mesh.bevel", text="Bevel")
        row02.operator("mesh.bridge_edge_loops", text="Bridge")
        row02.operator("mesh.solidify", text="Solidify")
        row03 = group01.row(align=True)
        row03.operator("mesh.extrude_faces_move", text="Extrude")
        row03.operator("mesh.extrude_faces_indiv", text="Indv")
        row03.operator("mesh.extrude_region_move", text="Region")
        
        ## row03.operator("mesh.dupli_extrude_cursor", text="Cursor").rotate_source = False
        row03.operator("mesh.flip_normals", text="Flip")


def DomPie_ObjectMode(pie, context):
    pie.operator("wm.search_menu", text="Search", icon='VIEWZOOM')
    pie.operator("object.delete", text="Delete Object", icon='CANCEL')
    DomPie_ManipulatorBox(pie, context)
    DomPie_ShelfAndProps(pie, context)
    DomPie_Add(pie, context)
    pie.operator_menu_enum("object.origin_set", "type")
    DomPie_MeshEditModes(pie, context)
    DomPie_SelectOptions(pie, context)
        
    #    space_data.transform_orientation
    # select
    # mirror
    # cursor
    # parent
    # group
    # align

def DomPie_SkipSlot(pie, context, layout):
    pie = pie.row()
    pie.label('')
    pie = layout.menu_pie()    

def DomPie_Bottom(pie, context, layout):
    DomPie_ManipulatorBox(pie, context)
    
def DomPie_BottomLeft(pie, context, layout):
    DomPie_MeshEditModes(pie, context)
    
def DomPie_Left(pie, context, layout):
    if context.mode == 'OBJECT':
        DomPie_SkipSlot(pie, context, layout)
    elif context.mode == "EDIT_MESH":
        DomPie_EditMeshCommonSelectionOps(pie, context)
    else:
        DomPie_SkipSlot(pie, context, layout)
    
def DomPie_TopLeft(pie, context, layout):
    DomPie_SkipSlot(pie, context, layout)
    
def DomPie_Top(pie, context, layout):
    pie.operator("wm.search_menu", text="Search", icon='VIEWZOOM')
    
def DomPie_TopRight(pie, context, layout):
    DomPie_SelectAddDelete(pie, context)
    
def DomPie_Right(pie, context, layout):
    if context.mode == 'OBJECT':
        DomPie_SkipSlot(pie, context, layout)
    elif context.mode == "EDIT_MESH":
        DomPie_EditMeshCommonEditOps(pie, context)
    else:
        DomPie_SkipSlot(pie, context, layout)

def DomPie_BottomRight(pie, context, layout):
    DomPie_ShelfAndProps(pie, context)


class DomPieBuilder(Menu):
    bl_idname = "pie.dom.builder"
    bl_label = "Build Dynamic Spacebar Pie"
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        # don't process if it's in the text editor. help with using alt+p in the text editor
        if type(context.area.spaces.active) == bpy.types.SpaceTextEditor:
            return
        DomPie_Left(pie, context, layout)
        DomPie_Right(pie, context, layout)
        DomPie_Bottom(pie, context, layout)
        DomPie_Top(pie, context, layout)
        DomPie_TopLeft(pie, context, layout)
        DomPie_TopRight(pie, context, layout)
        DomPie_BottomLeft(pie, context, layout)
        DomPie_BottomRight(pie, context, layout)

class DomsDynamicNoobSpacePieOp(bpy.types.Operator):
    """Op to build the dynamic pie"""
    bl_idname = "pie.dynamic_spacebar_pie"
    bl_label = "Dynamic Spacebar Pie"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="pie.dom.builder")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(DomsDynamicNoobSpacePieOp)
    bpy.utils.register_class(DomPieBuilder)
    bpy.utils.register_class(InstantVertexMode)
    bpy.utils.register_class(InstantEdgeMode)
    bpy.utils.register_class(InstantFaceMode)
    # add space bar keyboard shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('pie.dynamic_spacebar_pie', 'SPACE', 'PRESS')
    DomPie_LoadIcons()

def unregister():
    bpy.utils.unregister_class(DomsDynamicNoobSpacePieOp)
    bpy.utils.unregister_class(DomPieBuilder)
    bpy.utils.unregister_class(InstantVertexMode)
    bpy.utils.unregister_class(InstantEdgeMode)
    bpy.utils.unregister_class(InstantFaceMode)
    # remove space bar keyboard shortcut
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['3D View']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu_pie':
                if kmi.properties.name == "DomsDynamicNoobSpacePie":
                    km.keymap_items.remove(kmi)
                    print("removed")
                    break
    DomPie_UnloadIcons()

if __name__ == "__main__":
    register()
    bpy.ops.wm.call_menu_pie(name="pie.dom.builder")

# http://blenderlounge.fr/forum/viewtopic.php?f=26&t=732&start=60
# https://github.com/TazTako/A4B/blob/master/Atelier4blender.py

# todo snapping, fullscreen, shading, UV, vert paint, texture paint, layouts, sculpting, retopo
