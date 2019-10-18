
# "Scatter" Add-on
# Copyright (C) 2019 Dorian Borremans aka BD3D
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# <pep8 compliant>


bl_info = {
    "name" : "Scatter [BD3D]",
    "author" : "BD3D",   
    "description" : "The scattering tool of 2.8",
    "blender" : (2, 80, 0),
    "location" : "Operator",
    "warning" : "",
    "category" : "Generic"
}

import bpy, os, ctypes, platform, webbrowser, bmesh, random, rna_keymap_ui, functools, math, locale, time
from bl_operators.presets import AddPresetBase
from bpy.types import Menu, Panel, Operator, PropertyGroup, Operator, AddonPreferences, PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty
from bpy.app.handlers import persistent
C = context = bpy.context

#########################################################################################
######################################################################################
# # # # # # # # # # # #                 STORAGE                # # # # # # # # # # # # 
######################################################################################
######################################################################################

######################################################################################
# # # # # # # # # # # #         ADDON PREF STORAGE             # # # # # # # # # # # # 
######################################################################################

class SCATTER_AddonPref(AddonPreferences):
    bl_idname = __name__
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    scatter_categories : EnumProperty(name='Categories',description='test',items =[('Presets','Presets','','COLLAPSEMENU',1),('Assets','Assets','','MOD_PARTICLES',2),('Prefs','Prefs','','MOD_HUE_SATURATION',3),('Infos','Infos','','FILE_TEXT',4),],default='Presets')
    scatter_is_not_batch : BoolProperty(name="selection is individual / selection is collection",subtype='NONE',default=True)
    scatter_is_auto    : BoolProperty(name="Automatic Asset Detection",subtype='NONE',default=False)
    scatter_particles_sys_name : StringProperty(name="particle system name",subtype='NONE',default="MyParticles")
    scatter_percentage   : IntProperty(name="Display Particles % on creation",subtype='NONE',default=100,min=0,max=100)
    scatter_is_bounds    : BoolProperty(name="Display as Bounds on creation (proxies immune)",subtype='NONE',default=False)
    scatter_is_not_disp  : BoolProperty(name="Hide from Display on creation",subtype='NONE',default=False)
    scatter_is_curve     : BoolProperty(name="Curve(s) Detection",subtype='NONE',default=False)
    scatter_is_camera    : BoolProperty(name="Cam Detection",subtype='NONE',default=False)

    scatter_always_hund  : BoolProperty(name="display percentage always on 100% when toggling",description="",default=False)

    scatter_bound_if_more  : IntProperty(name="Set obj display to bounds if more than n faces:",subtype='NONE',default=7500,min=10)
    scatter_perc_if_more   : IntProperty(name="Maximal allowed particle count (before automatic on display % reduction",subtype='NONE',default=111000,min=100)
    scatter_nodisp_if_more : IntProperty(name="Maximal allowed particle count (before automatic on display % reduction",subtype='NONE',default=2000000,min=1000)
    scatter_ui_is_tri      : BoolProperty(name="UI Use triangles instead of icons",description="",default=False)
    active_is_terrain      : BoolProperty(name="Constantly use the active object as Terrain",description="",default=False)

    #Expand on/off
    scatter_radar_is_open            : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #radar
    scatter_infodisp_is_open         : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=True) #radar
    scatter_op_is_open               : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #on creation op
    scatter_disp_is_open             : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #on creation display
    scatter_curv_is_open             : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #curve op
    scatter_curv_adv_is_open         : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #curve advance
    scatter_nois_is_open             : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #noise op
    scatter_sliders_is_open          : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) #sliders
    scatter_sliders_ob_is_open       : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) 
    scatter_sliders_curv_is_open     : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) 
    scatter_sliders_curv_adv_is_open : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) 
    scatter_proxy_is_open            : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) 
    scatter_proxy_inception_is_open  : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) 
    scatter_camera_is_open           : BoolProperty(name="Show Debug Tools",description="Expand me senpai",default=False) 
    scatter_is_cam_zone              : BoolProperty(name="Show Debug Tools",description="",default=False) 
    scatter_is_paint                 : BoolProperty(name="Show Debug Tools",description="",default=False) 
    scatter_is_cloud                 : BoolProperty(name="Show Debug Tools",description="",default=False) 
    scatter_is_smart                 : BoolProperty(name="Show Debug Tools",description="",default=False) 
    scatter_is_warning               : BoolProperty(name="Show Debug Tools",description="",default=False) 
    scatter_is_paint_q               : BoolProperty(name="Show Debug Tools",description="",default=False) 
    scatter_show_scat_preview        : BoolProperty(name="Show Presets Previews",description="",default=True) 
    scatter_operator_is_open         : BoolProperty(name="Show Presets Previews",description="",default=True) 

    persquarem     : IntProperty(name=" ",subtype='NONE',default=100,min=0)
    persquaremorkm : EnumProperty(name="n particles per:",description=' ',items =[('/m²','/m²','','BLANK1',1),('/km²','/km²','','BLANK1',2),],default='/m²')

    batch_dis      : IntProperty(name=" ",subtype='NONE',default=100,min=0,max=100)
    batch_emi      : IntProperty(name=" ",subtype='NONE',default=100,min=0)
    batch_seed     : IntProperty(name=" ",subtype='NONE',default=0,min=0)
    batch_r_scale  : FloatProperty(name=" ",subtype='NONE',default=0,min=0,max=1)
    batch_r_rot    : FloatProperty(name=" ",subtype='NONE',default=0,min=0,max=2)
    batch_r_rot_tot: FloatProperty(name=" ",subtype='NONE',default=0,min=0,max=1)
    batch_t_idens  : FloatProperty(name=" ",subtype='NONE',default=0,min=0,max=1)
    batch_t_iscal  : FloatProperty(name=" ",subtype='NONE',default=0,min=0,max=1)
    batch_t_scal   : FloatProperty(name=" ",subtype='NONE',default=0,min=0)
    batch_t_off    : FloatProperty(name=" ",subtype='NONE',default=1,min=-100,max=100)
    batch_t_brigh  : FloatProperty(name=" ",subtype='NONE',default=1,min=0,max=2)
    batch_t_contr  : FloatProperty(name=" ",subtype='NONE',default=3,min=0,max=5)

    batch_curve_falloff    : FloatProperty(name=" ",subtype='NONE',default=0.5,min=0,max=10000)
    batch_curve_dist       : FloatProperty(name=" ",subtype='NONE',default=1.25,min=0,max=10000)
    batch_curve_infl       : FloatProperty(name=" ",subtype='NONE',default=1,min=0,max=1)

    particle_optimizer : IntProperty(name=" ",subtype='NONE',default=50,min=0,max=100)
    texture_enum_slots : EnumProperty(name=' ',description=' ',items =[('Slot01','Slot01','','TEXTURE_DATA',1),('Slot02','Slot02','','TEXTURE_DATA',2)],default='Slot01')


    region_refresh : BoolProperty(name="Refresh dummy",description="",default=False) 

######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne
######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne 
######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne
#             
#             oooooooooo.
#             `888'   `Y8b
#              888      888 oooo d8b  .oooo.   oooo oooo    ooo
#              888      888 `888""8P `P  )88b   `88. `88.  .8'
#              888      888  888      .oP"888    `88..]88..8'
#              888     d88'  888     d8(  888     `888'`888'
#             o888bood8P'   d888b    `Y888""8o     `8'  `8'
#             
#             
######################################################################################

######################################################################################
#      .o.             .o8        .o8         ooooooooo.                       .o88o.
#     .888.           "888       "888         `888   `Y88.                     888 `"
#    .8"888.      .oooo888   .oooo888          888   .d88' oooo d8b  .ooooo.  o888oo
#   .8' `888.    d88' `888  d88' `888          888ooo88P'  `888""8P d88' `88b  888
#  .88ooo8888.   888   888  888   888          888          888     888ooo888  888
# .8'     `888.  888   888  888   888          888          888     888    .o  888
#o88o     o8888o `Y8bod88P" `Y8bod88P"        o888o        d888b    `Y8bod8P' o888o
#
######################################################################################

    def draw(self, context):
        layout = self.layout
        full= "................................................................................................................................................................................................................................................................................................................................................................................................"
        addon_prefs = context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings

        bigbox = layout.box()
        bigbox.separator(factor=2.5)

        row = bigbox.row(align=True)
        row.prop(self, "scatter_categories", text="test",expand=True)
        row.scale_y = 1.5

#Input
#        if addon_prefs.scatter_categories == "Keymap":
#
#            text = bigbox.column()
#            text.label(text="")
#            text.scale_y=0.2
#
#            # shortbox = bigbox.box() #BIG PROBLEM WITH KEYMAP REGISTER. wtf
#            # col= shortbox.column()
#            # wm = bpy.context.window_manager
#            # kc = wm.keyconfigs.user #need to reference the actual keyconfig, ( referencing kc = wm.keyconfigs.addon won't be saved across sessions)
#            # km = kc.keymaps['Window']
#            # kmi = get_hotkey_entry_item(km,SCATTER_OT_C_Slots.bl_idname)
#            # if kmi:
#            #     col.context_pointer_set("keymap", km)
#            #     rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
#            #     col.separator()
#            #     col.label(text="Hotkey will be placed in User Preferences -> Keymap -> Window.")
#            # else:
#            #     col.label("No hotkey entry found")
#            #     col.operator(KbPiesAddHotkey.bl_idname, text = "Add hotkey entry", icon = 'ZOOMIN')

###############################################################################Custom Presets 

        if addon_prefs.scatter_categories == "Presets":

            bigbox.separator(factor=1.0)

            box = bigbox.box() ; box.separator(factor=0.05)

            col = box.box()
            dual_col = col.row()
            dual_col01 = dual_col.column() ; dual_col01.scale_y = 1.15 ;  dual_col01.scale_x = 1.75
            dual_col02 = dual_col.column()

            dual_col01.separator(factor=1.1)
            preset=dual_col01.row(align=True)
            preset.separator(factor=1.45)
            preset_op = preset.row(align=True)
            preset_op.operator(SCATTER_OT_C_Slots_del_confirm.bl_idname, text="", icon='TRASH')
            preset_op.operator(SCATTER_OT_C_Slots_Settings_reset.bl_idname, text="", icon='LOOP_BACK')
            preset.separator(factor=0.1)
            preset_enum = preset.box().row(align=True) ; preset_enum.scale_y = 0.75
            preset_enum.label(text=bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label.replace("_"," "))

            bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label
            preset.separator(factor=1.45)

            dual_col01.separator(factor=0.7)

            file = dual_col01.row(align=False) ; file.separator(factor=0.5)
            fileimp = file.row(align=True)
            fileimp.operator(SCATTER_OT_Open_Directory.bl_idname, text="Import / Export Folder", icon='FILEBROWSER')
            #fileimp.operator(SCATTER_OT_refresh_preview_debug.bl_idname, text="", icon='FILE_REFRESH')
            fileimp.operator(SCATTER_OT_refresh_preview_img.bl_idname, text="", icon='FILE_REFRESH')
            file.separator(factor=0.5)

            dual_col01.separator(factor=0.7)

            file = dual_col01.row(align=True); file.separator(factor=1.3)
            file.operator(SCATTER_OT_C_Slots_Quick_addpreset.bl_idname, text="New Preset From Settings Below", icon='FILE_TICK')
            file.separator(factor=1.3)

            image = dual_col02.row(align=True)
            preset_image = image.row(align=True) ; preset_image.scale_y = 0.66 ; preset_image.scale_x = 0.66
            preset_image.template_icon_view(context.window_manager,"my_previews",scale_popup=4,show_labels=True)
            preset_image.separator(factor=2.5)

            image = dual_col02.row(align=True)
            preset_op = image.row(align=True) ; preset_op.scale_x =1.5 ; preset_op.scale_y =0.85
            preset_op.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon='TRIA_LEFT_BAR').left0_right1  = 2
            preset_op.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon='TRIA_LEFT').left0_right1      = 0
            preset_op.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon='TRIA_RIGHT').left0_right1     = 1
            preset_op.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon='TRIA_RIGHT_BAR').left0_right1 = 3
            preset_op.separator(factor=1.0)

            box.separator(factor=0.1)
            line = box.row(align=True)
            line.label(text=full)
            line.scale_y=0.1
            
            col = box.column()
            col0 = col.box()
            col0.scale_y = 0.9
            col0.prop(C_Slots,"C_name")
            col0.prop(C_Slots,"C_desc")
            col0label = col0.column()
            col0label.label(text=C_Slots.C_desc)
            col0.scale_y = 1.3

            col.label(text=full)
            col1 = col.box()
            col1.scale_y = 0.9
            col3title = col1.row()
            col3title.label(text="Particles Settings:") #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX 
            col3title.alignment = 'CENTER'

            colr = col1.row(align=False)
            if (C_Slots.C_per_vert == False and C_Slots.C_per_face == False):
                colr.prop(C_Slots,"C_per_vert")
                colr.prop(C_Slots,"C_per_face")
            if C_Slots.C_per_vert == True:
                colr.prop(C_Slots,"C_per_vert")
                colr.label(text=" ")
            if C_Slots.C_per_face == True:
                colr.label(text=" ")
                colr.prop(C_Slots,"C_per_face")

            if (C_Slots.C_per_vert == False and C_Slots.C_per_face == False):
                row = col1.row(align=False)
                if C_Slots.C_countispersquare != 'None':
                    row.prop(C_Slots,"C_countpersquare")
                else:
                    row.prop(C_Slots,"C_count")
                rowR = row.row(align=True)
                rowR.prop(C_Slots,"C_countispersquare",text='test',expand=True)
                rowR.scale_x = 0.1

                if C_Slots.C_seed_is_random == True:
                    col1.prop(C_Slots,"C_seed_is_random")
                else:
                    col1.prop(C_Slots,"C_seed_is_random")
                    col1.prop(C_Slots,"C_seed")

                #col1.prop(C_Slots,"C_particle_size")
            col1row = col1.column(align= True)
            col1row.prop(C_Slots,"C_size_random", slider=True)
            col1row.prop(C_Slots,"C_phase_factor_random", slider=True)
            col1row.prop(C_Slots,"C_phase_rotation", slider=True)
            row = col1.row(align=False)
            row.prop(C_Slots,"C_orientation",expand=True)
            

            if (C_Slots.C_per_vert == False and C_Slots.C_per_face == False):
                col1.prop(C_Slots,"C_use_children")
                if C_Slots.C_use_children == True:
                    col1row = col1.column(align= True)
                    col1row.prop(C_Slots,"C_children_ammount")
                    col1row.prop(C_Slots,"C_children_roughness")
                    col1row.prop(C_Slots,"C_children_roughness_s")
                    col1row.prop(C_Slots,"C_children_clump")


            col.label(text=full)

            col3 = col.box()
            col3.scale_y = 0.9


            col3title = col3.row()
            col3title.label(text="Clustering Textures") 
            col3title.alignment = 'CENTER'

            col3row = col3.box().row()
            col3row.prop(addon_prefs,"texture_enum_slots", text="test",expand=True)
            col3row.scale_y = 1.5

            if addon_prefs.texture_enum_slots == "Slot01":

                #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
                #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
                #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX

                row3 = col3.box().row(align=True)
                row3.prop(C_Slots,"C_texture_type", text="test",expand=True)
                row3.scale_y = 1.5

                if (C_Slots.C_texture_type == "Automatic" or C_Slots.C_texture_type == "Texture"): #if C_Slots.C_texture_type == "Automatic2x":

                    col3.separator(factor=1.0)
                    col3row = col3.column(align=True)
                    col3row.prop(C_Slots,"C_density_factor", slider=True)
                    col3row.prop(C_Slots,"C_length_factor", slider=True)

                    col3.prop(C_Slots,"C_noise_randomtext")
                    if C_Slots.C_noise_randomtext == False:
                        col3row = col3.column(align=True)
                        col3row.prop(C_Slots,"C_intensity", slider=True)
                        col3row.prop(C_Slots,"C_contrast", slider=True)
                    col3.prop(C_Slots,"C_offset_is_random")

                    if C_Slots.C_offset_is_random == True:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_offset_A")
                        colal.prop(C_Slots,"C_offset_B")
                    else:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_offsetx")
                        colal.prop(C_Slots,"C_offsety")
                        colal.prop(C_Slots,"C_offsetz")

                    col3.prop(C_Slots,"C_size_is_random")
                    if C_Slots.C_size_is_random == True:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_size_A")
                        colal.prop(C_Slots,"C_size_B")
                    else:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_scalex")
                        colal.prop(C_Slots,"C_scaley")
                        colal.prop(C_Slots,"C_scalez")

                    if C_Slots.C_texture_type == "Automatic":

                        col3.prop(C_Slots,"C_noise_scaleisrandom")
                        if C_Slots.C_noise_scaleisrandom == True:
                            colal = col3.column(align=True)
                            colal.prop(C_Slots,"C_noise_scaleA")
                            colal.prop(C_Slots,"C_noise_scaleB")
                        else:
                            col3.prop(C_Slots,"C_noise_scale")
                        col3.prop(C_Slots,"C_use_band")
                        if C_Slots.C_use_band == True:  col3.prop(C_Slots,"C_band_turbulance")
                        elif C_Slots.C_use_band == False: col3.prop(C_Slots,"C_noise_depth")

                    elif C_Slots.C_texture_type == "Texture":

                        col3.prop(C_Slots,"C_texture_or_img1")
                        info = ""; texx=""
                        if C_Slots.C_texture_or_img1 == "Texture":
                            infos = "Does this texture above exist in the file?" ; texx = "Texture Name"
                        else: infos = "Does this image above exist in '__textures__'? (import/export folder)" ; texx = "Image Name + ext"
                        if C_Slots.C_texture_or_img1 != "Terrain":
                            col3row = col3.row(align=True)
                            col3row.prop(C_Slots,"C_texture_name1",text = texx)
                            col3row.operator(SCATTER_OT_slider_img_open_direct.bl_idname,text='',icon="FILE_FOLDER")
                            col3row.scale_x = 0.5

                            col3row = col3.row(align=True)
                            col3rowlab = col3row.row() ; col3rowlab.label(text="Projection:") ; col3rowlab.scale_x = 0.33
                            col3row.prop(C_Slots,"C_texture_uv1", icon="UV")   

                            col3.label(text=infos, icon='QUESTION')
                            col3.separator(factor=0.5)


            elif addon_prefs.texture_enum_slots == "Slot02":
                #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
                #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
                #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX

                row3 = col3.box().row(align=True)
                row3.prop(C_Slots,"C_texture_type2", text="test",expand=True)
                row3.scale_y = 1.5

                if (C_Slots.C_texture_type2 == "Automatic" or C_Slots.C_texture_type2 == "Texture"):

                    col3.separator(factor=1.0)
                    ol3title = col3.column(align=True)
                    ol3title.prop(C_Slots,"C_density_factor2", slider=True)
                    ol3title.prop(C_Slots,"C_length_factor2", slider=True)

                    col3.prop(C_Slots,"C_noise_randomtext2")
                    if C_Slots.C_noise_randomtext2 == False:
                        ol3title = col3.column(align=True)
                        ol3title.prop(C_Slots,"C_intensity2", slider=True)
                        ol3title.prop(C_Slots,"C_contrast2", slider=True)
                    col3.prop(C_Slots,"C_offset_is_random2")
                    if C_Slots.C_offset_is_random2 == True:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_offset_A2")
                        colal.prop(C_Slots,"C_offset_B2")
                    else:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_offsetx2")
                        colal.prop(C_Slots,"C_offsety2")
                        colal.prop(C_Slots,"C_offsetz2")
                    col3.prop(C_Slots,"C_size_is_random2")
                    if C_Slots.C_size_is_random2 == True:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_size_A2")
                        colal.prop(C_Slots,"C_size_B2")
                    else:
                        colal = col3.column(align=True)
                        colal.prop(C_Slots,"C_scalex2")
                        colal.prop(C_Slots,"C_scaley2")
                        colal.prop(C_Slots,"C_scalez2")

                    if C_Slots.C_texture_type2 == "Automatic":

                        col3.prop(C_Slots,"C_noise_scaleisrandom2")
                        if C_Slots.C_noise_scaleisrandom2 == True:
                            colal = col3.column(align=True)
                            colal.prop(C_Slots,"C_noise_scaleA2")
                            colal.prop(C_Slots,"C_noise_scaleB2")
                        else:
                            col3.prop(C_Slots,"C_noise_scale2")
                        col3.prop(C_Slots,"C_use_band2")
                        if C_Slots.C_use_band2 == True:
                            col3.prop(C_Slots,"C_band_turbulance2")
                        elif C_Slots.C_use_band2 == False:
                            col3.prop(C_Slots,"C_noise_depth2")

                    elif C_Slots.C_texture_type2 == "Texture":


                        col3.prop(C_Slots,"C_texture_or_img2")
                        info = ""; texx=""
                        if C_Slots.C_texture_or_img2 == "Texture":
                            infos = "Does this texture above exist in the file?" ; texx = "Texture Name"
                        else: infos = "Does this image above exist in '__textures__'? (import/export folder)" ; texx = "Image Name + ext"
                        if C_Slots.C_texture_or_img2 != "Terrain":
                            col3row = col3.row(align=True)
                            col3row.prop(C_Slots,"C_texture_name2",text = texx)
                            col3row.operator(SCATTER_OT_slider_img_open_direct.bl_idname,text='',icon="FILE_FOLDER")
                            col3row.scale_x = 0.5

                            col3row = col3.row(align=True)
                            col3rowlab = col3row.row() ; col3rowlab.label(text="Projection:") ; col3rowlab.scale_x = 0.33
                            col3row.prop(C_Slots,"C_texture_uv2", icon="UV")

                            col3.label(text=infos, icon='QUESTION')
                            col3.separator(factor=0.5)

###############################################################################Assets
        if addon_prefs.scatter_categories == "Assets":

            text = bigbox.column()
            text.label(text="on construction",icon="EXPERIMENTAL")
            text.scale_y=0.2
                

###############################################################################Prefs
        if addon_prefs.scatter_categories == "Prefs":

            text = bigbox.column()
            text.label(text="")
            text.scale_y=0.2

            col = bigbox.box()
            col.label(text="Addon UI:", icon="COLOR")
            col.prop(addon_prefs,"scatter_ui_is_tri")

            col = bigbox.box()
            col.label(text="Thumbnails Scenes:", icon="FILE_IMAGE")
            col.operator(SCATTER_OT_import_thumbnail_scene.bl_idname, text="Add Thumbnail scene to file Scenes")


###############################################################################Notes
        if addon_prefs.scatter_categories == "Notes":

            text = bigbox.column()
            text.label(text="")
            text.scale_y=0.2

            notebox = bigbox.box()
            notebox.label(text="FAQ")
            coll = notebox.column()
            coll.operator('wm.url_open', text="Blender Artsit Thread", icon='URL').url = "https://blenderartists.org/t/auto-clustering-scattering-addon/1177672"
            coll.operator('wm.url_open', text="Youtube Tutorial", icon='URL').url = "https://www.youtube.com/?app=desktop"

            notebox.label(text="Autor: [DB3D]")
            coll = notebox.column()
            coll.operator('wm.url_open', text="Follow me on Twitter", icon='URL').url = "https://twitter.com/dorianborremans?lang=en"
            coll.operator('wm.url_open', text="Check out my Artstation", icon='URL').url = "https://www.artstation.com/dorianborremans"
            coll.operator('wm.url_open', text="My other Addons/Products", icon='URL').url = "https://blendermarket.com/creators/bd3d-store"


######################################################################################
#   
#   ooooooooo.   ooooooooooooo       .oooooo..o                         .       .
#   `888   `Y88. 8'   888   `8      d8P'    `Y8                       .o8     .o8
#    888   .d88'      888           Y88bo.       .ooooo.   .oooo.   .o888oo .o888oo  .ooooo.  oooo d8b
#    888ooo88P'       888            `"Y8888o.  d88' `"Y8 `P  )88b    888     888   d88' `88b `888""8P
#    888              888                `"Y88b 888        .oP"888    888     888   888ooo888  888
#    888              888           oo     .d8P 888   .o8 d8(  888    888 .   888 . 888    .o  888
#   o888o            o888o          8""88888P'  `Y8bod8P' `Y888""8o   "888"   "888" `Y8bod8P' d888b
#   
######################################################################################


class SCATTER_PT_Scatter_OP(bpy.types.Panel):
    bl_idname = "SCATTER_PT_Scatter_OP" 
    bl_label = "Scatter Operator"
    bl_category = "Scatter BETA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        layout = self.layout
        A      = C_Slots.Terrain_pointer
        box=layout #in case if whole panel in a box ? 


        ### ### ### ### ### ### SCATTER OPERATOR
        ### ### ### ### ### ### SCATTER OPERATOR
        ### ### ### ### ### ### SCATTER OPERATOR
        na = "Scatter"
        if addon_prefs.scatter_ui_is_tri == False: na = "V   "+na if addon_prefs.scatter_operator_is_open else ">   "+na
        ixon = "PARTICLE_DATA" 
        if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_operator_is_open else "DISCLOSURE_TRI_RIGHT"

        row = box.row(align=True) ; row.scale_y = 1.21##
        row.alignment = 'LEFT'
        row.prop(addon_prefs,'scatter_operator_is_open',text=na,emboss=False,icon=ixon)
        if addon_prefs.scatter_operator_is_open:

            ### BUTTON + PRESET
            button_box = box#.box()
            bothrow= button_box.row(align=True) ; bothrow.scale_y=1.9
            bothrow.separator(factor=2.0)
            bigbutton = bothrow.column(align=True)
            no = ""
            if C_Slots.Terrain_pointer == None: bigbutton.enabled=False ; no = "[Please Asign a Target]"
            elif bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label == "Please choose a Preset": bigbutton.enabled=False ; no = "[Please choose a Preset]"
            bigbutton.operator(SCATTER_OT_C_Slots.bl_idname, text="SCATTER" if no == "" else no,  icon='PARTICLES')
            pref = bothrow.column(align=True) ; pref.scale_x = 1.2
            pref.operator(SCATTER_OT_parameter.bl_idname, text="",  icon='PREFERENCES')
            #bigbutton.prop(addon_prefs,'scatter_is_not_batch',text='',icon='GROUP'if addon_prefs.scatter_is_not_batch is True else 'LONGDISPLAY')

            trirow = button_box.row()
            trirow.separator(factor=0.7)
            col = trirow.box().column()

            col.separator(factor=0.7)

            Targetrow = col.row()
            Targetrow.separator(factor=1.0)
            Targetbox = Targetrow.box() ; Targetbox.scale_y = 1.4
            Targetrow.separator(factor=1.0)
            Targetbox.separator(factor=0.1)
            Target = Targetbox.row(align=True)
            Target.separator(factor=1)
            Targetlab = Target.column()
            Targetlab.scale_x = 0.75
            Targetlab.label(text="Target: ",icon="TRACKER")
            Target.prop(C_Slots,'Terrain_pointer',text='')
            Target.operator(SCATTER_OT_active_to_target.bl_idname, text="" ,icon="SELECT_SET")
            Targetbox.separator(factor=0.1)

            #Targetcoloprow.operator(SCATTER_OT_terrain_is_active.bl_idname, text="" ,icon="RESTRICT_SELECT_OFF")
            #if addon_prefs.active_is_terrain == True: Targetcoloprowop.enabled = False ; Targetcoltt.enabled = False
            Target.separator(factor=1.35)

            coll=col.column(align=False)

            #name.prop(addon_prefs,"scatter_show_scat_preview",text="",icon="SEQ_PREVIEW") 
            coll.separator(factor=1.3)
            row = coll.row(align=True)
            row.separator(factor=2)
            image = row.column()
            if addon_prefs.scatter_show_scat_preview == True: #wab need to hide if crash ? 
                #if C_Slots.Terrain_pointer == None: coll.enabled=False
                image.template_icon_view(context.window_manager,"my_previews",scale=7,show_labels=True,scale_popup=5)
            row.separator(factor=2)
            coll.separator(factor=0)

            image.separator(factor=1)

            preset = image.row(align=True)
            preset_label = preset.box()
            rowb = preset_label.row()
            rowb.label(text="")
            presetn =  rowb.row(align=True) ; presetn.alignment = 'CENTER'
            presetn.label(text=bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label.replace("_"," "))
            rowb.label(text="")

            skip = image.row(align=True)
            skip.scale_y = 0.85
            skip.scale_x = 5
            skip.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon="TRIA_LEFT_BAR").left0_right1  = 2
            skip.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon="TRIA_LEFT").left0_right1      = 0 
            skip.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon="TRIA_RIGHT").left0_right1     = 1 
            skip.operator(SCATTER_OT_skip_prev.bl_idname, text="", icon="TRIA_RIGHT_BAR").left0_right1 = 3

            name = image.row(align=False)
            name.prop(addon_prefs,'scatter_particles_sys_name',text='')

            coll.separator(factor=1.5)
            button_box.separator(factor=0.2)



        ### ### ### ### ### ### RADAR
        ### ### ### ### ### ### RADAR
        ### ### ### ### ### ### RADAR
        na = "Selection Radar" 
        if addon_prefs.scatter_ui_is_tri == False: na = "V   "+na if addon_prefs.scatter_radar_is_open else ">   "+na
        ixon = "VIS_SEL_11" 
        if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_radar_is_open else "DISCLOSURE_TRI_RIGHT"

        row = box.row(align=True) ; row.scale_y = 1.21##
        row.alignment = 'LEFT'
        row.prop(addon_prefs,'scatter_radar_is_open',text=na,emboss=False,icon=ixon) 

        if addon_prefs.scatter_radar_is_open == True:
            sliderbox=box.box()
            if C_Slots.Terrain_pointer == None: sliderbox.enabled = False

            col = sliderbox.column()
            #col.prop(addon_prefs,"scatter_is_auto", text="Detect Smart Asset(s)", toggle=False)
            col.prop(addon_prefs,"scatter_is_curve", text="Detect and auto execute Boolean(s)", toggle=False)
            col.prop(addon_prefs,"scatter_is_camera", text="Detect and auto execute Camera as Clip/Cull", toggle=False)

            label=sliderbox.box().column()
            label.scale_y=1.2
            prox_will_fail = False
            computer_inten = False

            if C_Slots.Terrain_pointer != None:
                S = bpy.context.selected_objects

                labelduo=label.box().row()
                labelduo.label(text='"'+C_Slots.Terrain_pointer.name +'"', icon='TRACKER')
                labelduo.label(text='As Target')

                prox_in_S = False
                for obj in S:
                    if "[proxy]" in obj.name: prox_in_S = True ; break

                count = 0

                if prox_in_S is False:
                    for ob in S:
                        if (ob != A and ob.type =='MESH'):
                            labelduo=label.row()
                            labelduo.label(text='"'+ob.name +'"', icon='MOD_PARTICLES')
                            labelduo.label(text='As Particles')

                        if addon_prefs.scatter_is_camera == True :
                            if ob.type == 'CAMERA': 
                                count += 1
                                if count == 1:
                                    labelduo=label.row()
                                    labelduo.label(text='"Camera"', icon='OUTLINER_OB_CAMERA')
                                    labelduo.label(text='As Clip/Cull')
                                    computer_inten = True

                        if addon_prefs.scatter_is_curve == True :
                            if ob.type == 'CURVE': 
                                labelduo=label.row()
                                labelduo.label(text='"'+ob.name +'"', icon='SELECT_SUBTRACT')
                                labelduo.label(text='As Boolean')
                                computer_inten = True

                else:
                    for ob in S:
                        if (ob != A and ob.type =='MESH' and '[proxy]' not in ob.name): #for non prox obj
                            have_prox_in_S = False
                            for o in S:
                                if o.name == ob.name +" [proxy]": have_prox_in_S = True
                            if have_prox_in_S == False:
                                labelduo=label.row()
                                labelduo.label(text='"'+ob.name +'"', icon='ERROR') #MOD_PARTICLES
                                labelduo.label(text='Missing Proxy')#, icon='ERROR')
                                prox_will_fail = True
                            else:
                                labelduo=label.row()
                                labelduo.label(text='"'+ob.name +'"', icon='SHADING_BBOX')
                                labelduo.label(text='As Particles + [proxy]')

                        if (ob != A and ob.type =='MESH' and '[proxy]' in ob.name):
                            have_obj_in_S = False
                            for o in S:
                                if o.name == ob.name[:-8]: have_obj_in_S = True
                            if have_obj_in_S == False:
                                labelduo=label.row()
                                labelduo.label(text='"'+ob.name +'"', icon='ERROR') #OBJECT_HIDDEN
                                labelduo.label(text='Missing Render Obj')#, icon='ERROR')
                                prox_will_fail = True

                        if addon_prefs.scatter_is_curve == True :
                            if ob.type == 'CURVE': 
                                labelduo=label.row()
                                labelduo.label(text='"'+ob.name +'"', icon='SELECT_SUBTRACT')
                                labelduo.label(text='As Boolean')
                                computer_inten = True

                        if addon_prefs.scatter_is_camera == True :
                            if ob.type == 'CAMERA': 
                                count += 1
                                if count == 1:
                                    labelduo=label.row()
                                    labelduo.label(text='"Camera"', icon='OUTLINER_OB_CAMERA')
                                    labelduo.label(text='As Clip/Cull')
                                    computer_inten = True

                if len(S) == 0: label.label(text='have at least one meshes in selection', icon='ERROR')
            else: label.label(text='Please Asign a terrain Target', icon='ERROR')
            if prox_will_fail == True: col = sliderbox.column(); col.label(text='each assets need their own proxies', icon='ERROR')
            if computer_inten == True: col = sliderbox.column(); col.label(text='May be too Heavy to compute at once', icon='ERROR')

        ### ### ### ### ### ### ON CREATION EMISSION
        ### ### ### ### ### ### ON CREATION EMISSION
        ### ### ### ### ### ### ON CREATION EMISSION
        na = "On Creation Emission"
        if addon_prefs.scatter_ui_is_tri == False: na = "V   "+na if addon_prefs.scatter_op_is_open else ">   "+na
        ixon = "IMGDISPLAY"
        if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_op_is_open else "DISCLOSURE_TRI_RIGHT"

        row = box.row(align=True) ; row.scale_y = 1.21##
        row.alignment = 'LEFT'
        row.prop(addon_prefs,'scatter_op_is_open',text=na,emboss=False,icon=ixon)
        if addon_prefs.scatter_op_is_open:
            sliderbox=box.box().column()
            if C_Slots.Terrain_pointer == None: sliderbox.enabled = False

            row = sliderbox.row(align=False)
            row.prop(C_Slots,"C_countispersquare",text=' ',expand=True)
            row.scale_y = 0.8
            sliderbox.separator(factor=0.5)
            row = sliderbox.row(align=False)
            if C_Slots.C_countispersquare != 'None': row.prop(C_Slots,"C_countpersquare") ; rowr = row.row(align=True) ; rowr.scale_x = 0.35 ; rowr.operator(SCATTER_OT_how_much.bl_idname, text=" ", icon="OUTLINER_OB_LIGHT")
            else: sliderbox.prop(C_Slots,"C_count")
            sliderbox.label(text="automatic actions will be executed if emission count is too high",icon='QUESTION')

        ### ### ### ### ### ### ON DISPLAY
        ### ### ### ### ### ### ON DISPLAY
        ### ### ### ### ### ### ON DISPLAY
        na = "On Creation Display"
        if addon_prefs.scatter_ui_is_tri == False: na = "V   "+na if addon_prefs.scatter_disp_is_open else ">   "+na
        ixon = "RESTRICT_VIEW_OFF"
        if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_disp_is_open else "DISCLOSURE_TRI_RIGHT"

        row = box.row(align=True) ; row.scale_y = 1.21##
        row.alignment = 'LEFT'
        row.prop(addon_prefs,'scatter_disp_is_open',text=na,emboss=False,icon=ixon)
        if addon_prefs.scatter_disp_is_open:
            sliderbox=box.box()
            if C_Slots.Terrain_pointer == None: sliderbox.enabled = False

            boxx = sliderbox.column()
            boxx.prop(addon_prefs,"scatter_percentage")
            boxx.separator()
            boxx.prop(addon_prefs,"scatter_is_bounds")
            boxx.prop(addon_prefs,"scatter_is_not_disp")
            boxx.separator()

            slid=boxx.row(align=False)
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_infodisp_is_open',text="Automatic actions",emboss=False,icon="PREFERENCES")
            if addon_prefs.scatter_infodisp_is_open:
                boxbox=boxx.box().column()
                boxbox.label(text="if your particle polycount is above A, Scatter will automatically use bounding boxes for you")
                boxbox.prop(addon_prefs,"scatter_bound_if_more",text="A")
                boxbox.label(text="if your emission number is above B, Scatter will automatically lower the display % for you")
                boxbox.prop(addon_prefs,"scatter_perc_if_more",text="B")
                boxbox.label(text="if your emission number is above C, Scatter willautomatically hide thoses ps for you")
                boxbox.prop(addon_prefs,"scatter_nodisp_if_more",text="C")

        ### ### ### ### ### ### SCATTER ASSETS
        ### ### ### ### ### ### SCATTER ASSETS
        ### ### ### ### ### ### SCATTER ASSETS
        na = "Scatter Assets"
        if addon_prefs.scatter_ui_is_tri == False: na = "V   "+na if addon_prefs.scatter_is_smart else ">   "+na
        ixon = "HAIR"
        if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_is_smart else "DISCLOSURE_TRI_RIGHT"

        row = box.row(align=True) ; row.scale_y = 1.21##
        row.alignment = 'LEFT'
        row.prop(addon_prefs,'scatter_is_smart',text=na,emboss=False,icon=ixon)
        if addon_prefs.scatter_is_smart:
            sliderbox=box.box()
            if C_Slots.Terrain_pointer == None: sliderbox.enabled = False
            sliderbox.label(text="on construction",icon="EXPERIMENTAL")
            



######################################################################################
# 
# ooooooooo.   ooooooooooooo      ooooooooo.                          .    o8o            oooo
# `888   `Y88. 8'   888   `8      `888   `Y88.                      .o8    `"'            `888
#  888   .d88'      888            888   .d88'  .oooo.   oooo d8b .o888oo oooo   .ooooo.   888   .ooooo.   .oooo.o
#  888ooo88P'       888            888ooo88P'  `P  )88b  `888""8P   888   `888  d88' `"Y8  888  d88' `88b d88(  "8
#  888              888            888          .oP"888   888       888    888  888        888  888ooo888 `"Y88b.
#  888              888            888         d8(  888   888       888 .  888  888   .o8  888  888    .o o.  )88b
# o888o            o888o          o888o        `Y888""8o d888b      "888" o888o `Y8bod8P' o888o `Y8bod8P' 8""888P'
# 
######################################################################################


class SCATTER_PT_slider(bpy.types.Panel):
    bl_idname = "SCATTER_PT_slider"
    bl_label = "Terrain Particles"
    bl_category = "Scatter BETA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings
        A           = C_Slots.Terrain_pointer
        box         = layout

        colL = box.row(align=True)
        colL.separator(factor=1.5)
        col = colL.box().column(align=True)
        colset = box.column(align=True)
        col.scale_y=1.2

        is_1_num=-1
        #verification system how many slots are currently "selected"
        sc_count=0
        is_activ=""

       ######################################################### PARTICLES SELECTION 
       ######################################################### PARTICLES SELECTION 
       ######################################################### PARTICLES SELECTION 

        col.separator(factor=1.0)
        if A != None:
            is_1_num=0
            if A.type == 'MESH':
                for ob in A.particle_systems:
                    if "SCATTER" in ob.name: ####
                        sc_count +=1
                        if ob.name in A.modifiers:
                            row=col.row(align=True)
                            if bpy.data.particles[ob.name]["is_selected"] == 1: row.label(icon="PLAY") ; is_1_num +=1 ; is_activ = ob.name 
                            else: row.label(icon="BLANK1")
                                
                            #is_1 =0 #again same verification, may be useless could do with is_1_num ? but it's working fine so don't care
                            #for bool in A.particle_systems:
                            #    if "SCATTER" in bool.name: is_1 += bpy.data.particles[bool.name]["is_selected"]
          
                            row.operator(SCATTER_OT_slider_boolean.bl_idname, text=ob.name[9:]).property_1 = ob.name
                            row.prop(A.modifiers[ob.name],"show_viewport",text="")
                            row.prop(A.modifiers[ob.name],"show_render",text="")
                            row.operator(SCATTER_OT_slider_remov_system.bl_idname, text="",icon='REMOVE').remov_obj = ob.name
                            row.separator(factor=0.6)
                            row.scale_y=1.2
        else: label=col.row(align=True) ; label.label(text="",icon="BLANK1") ; label.box().label(text="  Please Asign a Target",icon="TRACKER")
        if (sc_count is 0 and A!= None): label=col.row(align=True) ; label.label(text="",icon="BLANK1") ; label.box().label(text="  Please Create a Particle System",icon="PARTICLES")
        if sc_count == 0: is_1_num=-1
        col.separator(factor=0.75)

        if A== None:        
            nam = "No Target Assigned"
            if addon_prefs.scatter_ui_is_tri == False:  nam = " >   " + nam
        elif sc_count == 0: 
            nam = "No Particles Created"
            if addon_prefs.scatter_ui_is_tri == False:  nam = " >   " + nam
        elif is_1_num == 0: 
            nam = "No System(s) Selected"
            if addon_prefs.scatter_ui_is_tri == False:  nam = " >   " + nam
        elif is_1_num > 1:
            nam = "Multiples Systems Not Supported"
            if addon_prefs.scatter_ui_is_tri == False:  nam = " >   " + nam

       ######################################################### SLIDERS 
       ######################################################### SLIDERS 
       ######################################################### SLIDERS 

        if is_1_num == 1:
            na = "Sliders" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_sliders_is_open else ">   "+na
            ixon = "MOD_HUE_SATURATION"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_sliders_is_open else "DISCLOSURE_TRI_RIGHT"
     
            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_sliders_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_sliders_is_open:

                act_sys = bpy.data.particles[is_activ]

                colset = layout.column()
                colset.scale_y = 0.95

                colset.separator()
                colse=colset.box()
                colse.label(text="Display:")
                colse.prop(A.particle_systems[act_sys.name].settings,"display_percentage",text="display %")

                colset.separator()
                colse=colset.box()
                colse.label(text="Particles:")   
     
                colsecolcol = colse.column(align=True)
                colsebit = colsecolcol.row(align=True)
                colsebit.prop(addon_prefs,"persquaremorkm", expand=True)
                colsebit.operator(SCATTER_OT_how_much2.bl_idname,text="",icon="OUTLINER_OB_LIGHT")
     
                colserow=colsecolcol.row(align=True)
                colserow.prop(addon_prefs,"persquarem",text="emission Density per  "+addon_prefs.persquaremorkm)
                colserowrow=colserow.row(align=True)
                colserowrow.operator(SCATTER_OT_slider_persquaremeters.bl_idname,text="apply").persquare_obj = act_sys.name
                colserowrow.scale_x = 0.3

                colsecolcol.prop(A.particle_systems[act_sys.name].settings,"count",text="emission number")
                #colse.separator(factor=0.5)
                colserow=colsecolcol.row(align=True)
                colserow.prop(A.particle_systems[act_sys.name],"seed",text="seed value")
                colserowrow=colserow.row(align=True)
                colserowrow.operator(SCATTER_OT_slider_batch_seed_random.bl_idname, text="randomize")
                colserowrow.scale_x = 0.3

                colse.label(text="Transformation:")
     
                colcol = colse.column(align=True)
                colcol.prop(A.particle_systems[act_sys.name].settings,"size_random",text="random scale")
                colcol.prop(A.particle_systems[act_sys.name].settings,"phase_factor_random",text="random rotation Z")
                colcol.prop(A.particle_systems[act_sys.name].settings,"rotation_factor_random",text="random rotation")

                rowrow = colcol.row(align=True)
                ap = rowrow.operator(SCATTER_OT_particles_orientation.bl_idname, text="Zglobal") ; ap.option = "GLOB_Z"
                bp = rowrow.operator(SCATTER_OT_particles_orientation.bl_idname, text="Hair")    ; bp.option = "VEL"
                cp = rowrow.operator(SCATTER_OT_particles_orientation.bl_idname, text="Znormal") ; cp.option = "NOR"
                dp = rowrow.operator(SCATTER_OT_particles_orientation.bl_idname, text="Zlocal")  ; dp.option = "OB_Z"              
                colset.separator()
                
                colsettt=colset.box()
                colsettt.label(text="Texture:")

                s1 = A.particle_systems[act_sys.name].settings.texture_slots[0]
                s2 = A.particle_systems[act_sys.name].settings.texture_slots[1]
                if (s1 == None or s1.name =="") and (s2 == None or s2.name ==""):
                    colsettt.operator(SCATTER_OT_slider_create_tex.bl_idname, text="create a new texture").name_1 = act_sys.name
                else:
                    sl=1 if s2 == None or s2.name =="" else 2
                    i=0

                    if sl==2:
                        colsettt.label(text="Calculating two texture is too hard for blender, refresh for accurate result",icon="QUESTION")
                        colsett_enum_row =colsettt.row(align=True)
                        colsett_enum_row.prop(addon_prefs,"texture_enum_slots",expand=True)
                        colsett_enum_row.scale_y = 1.4
 
                    for a in range(sl):
                        if addon_prefs.texture_enum_slots == 'Slot0'+str(i+1):


                            if A.particle_systems[act_sys.name].settings.texture_slots[i].texture.type != 'IMAGE':
                                ratio = 0.5+(i + 1 + addon_prefs.region_refresh)/3
                                preview=colsettt.row()
                                preview.separator(factor=ratio)
                                preview.template_preview(A.particle_systems[act_sys.name].settings.texture_slots[i].texture)
                                preview.enabled = False
                                preview.separator(factor=ratio)

                            if A.particle_systems[act_sys.name].settings.texture_slots[i].texture.type == 'IMAGE':

                                preview=colsettt.row()
                                ratio = 0.5+(i + 1  + addon_prefs.region_refresh)/3
                                preview.separator(factor=0.5)
                                preview.template_icon_view(context.window_manager,"my_textures",scale=5,show_labels=True,scale_popup=5)
                                preview.separator(factor=ratio)
                                renderpreview = preview.column()
                                renderpreview.separator(factor=1.5)
                                renderpreview.template_preview(A.particle_systems[act_sys.name].settings.texture_slots[i].texture)
                                renderpreview.enabled = False
                                renderpreview.scale_y=0.9
                                preview.separator(factor=ratio)

                                img_op = colsettt.row(align=True) ; img_op.scale_y = 1.2

                                ttt = img_op.operator(SCATTER_OT_slider_img_enum_choose.bl_idname,text='apply')
                                ttt.particle_name = act_sys.name ; ttt.i = i
                                img_op.separator()
                                img_op.operator(SCATTER_OT_refresh_preview_img.bl_idname,text='',icon="FILE_REFRESH")
                                img_op.operator(SCATTER_OT_slider_img_open_direct.bl_idname,text='',icon="FILE_FOLDER")
                                img_op.separator()
                                tb=img_op.operator(SCATTER_OT_img_skip_prev.bl_idname,text='',icon='TRIA_LEFT')
                                ta=img_op.operator(SCATTER_OT_img_skip_prev.bl_idname,text='',icon='TRIA_RIGHT')
                                tb.left0_right1 = 0 ; ta.left0_right1 = 1 ; ta.particle_name =  tb.particle_name = act_sys.name ; ta.i = tb.i = i
                                
                                proj = colsettt.row(align=True)
                                projlab = proj.row(align=True)
                                projlab.label(text="Image:")
                                projlab.scale_x = 0.35
                                proj.prop(A.particle_systems[act_sys.name].settings.texture_slots[i].texture,"image",text="")
                                if A.particle_systems[act_sys.name].settings.texture_slots[i].texture.image != None: 
                                    t = proj.operator(SCATTER_OT_slider_img_create_invert.bl_idname,text='',icon="ARROW_LEFTRIGHT")
                                    t.img = A.particle_systems[act_sys.name].settings.texture_slots[i].texture.image.name
                                    t.particle_name = act_sys.name
                                    t.i = i

                                proj = colsettt.row()
                                proj.prop(A.particle_systems[act_sys.name].settings.texture_slots[i],"texture_coords",text="projection:")

                            colsetttcol = colsettt.column(align=True)
                            colsetttcol.prop(A.particle_systems[act_sys.name].settings.texture_slots[i],"density_factor",text="density influence",slider=True)
                            colsetttcol.prop(A.particle_systems[act_sys.name].settings.texture_slots[i],"length_factor",text="scale influence",slider=True)
     
                            colsetttcol = colsettt.column(align=True)
                            colsetttcol.prop(bpy.data.textures[A.particle_systems[act_sys.name].settings.texture_slots[i].name],"intensity",text="color brightness",slider=True)
                            colsetttcol.prop(bpy.data.textures[A.particle_systems[act_sys.name].settings.texture_slots[i].name],"contrast",text="color contrast",slider=True)
                            
                            colrow = colsettt.split()
                            colrow1=colrow.column(align=True)
                            colrow2=colrow.column(align=True)
                            colrow1.prop(A.particle_systems[act_sys.name].settings.texture_slots[i],"scale",text="Texture Scale")
                            colrow2.prop(A.particle_systems[act_sys.name].settings.texture_slots[i],"offset",text="Texture Offset")
                        i+=1
     
                if A.particle_systems[act_sys.name].settings.child_type == 'INTERPOLATED':
                    colset.separator()
                    colsett=colset.box().column(align=True)
                    colsett.label(text="Childs:")
                    colsett.prop(A.particle_systems[act_sys.name].settings,"rendered_child_count",text="render child ammount")
                    colsett.prop(A.particle_systems[act_sys.name].settings,"child_nbr",text="display child ammount")
                    colsett.prop(A.particle_systems[act_sys.name].settings,"roughness_1",text="roughness intensity")
                    colsett.prop(A.particle_systems[act_sys.name].settings,"roughness_1_size",text="roughness size")
                    colsett.prop(A.particle_systems[act_sys.name].settings,"clump_factor",text="clumping")
     
                colset.separator()
                colsett=colset.box()
                colsett.label(text="Mandatory Vgroup:")
                if "INVERT:"+act_sys.name[9:] not in A.modifiers:
                    ixon = "BLANK1"
                else:
                    if A.modifiers["INVERT:"+act_sys.name[9:]].show_render == False: ixon = "BLANK1"
                    else:  ixon = "ARROW_LEFTRIGHT"
                boxrow = colsett.box().row()
                boxrow.label(text='"'+A.particle_systems[act_sys.name].vertex_group_density+'"',icon='GROUP_VERTEX')
                op = boxrow.operator(SCATTER_OT_inverseinfluence.bl_idname,text='', icon=ixon )
                op.just_create = False ; op.of_this_one = act_sys.name[9:]

        ######################################################### SLIDER BATCH
        ######################################################### SLIDER BATCH
        ######################################################### SLIDER BATCH

        elif (is_1_num > 1 or is_1_num == 0):
            enabled = True
            na = "Sliders Batch" 
            if sc_count == 0:   na = "No Particles Yet"      ; enabled = False
            elif is_1_num == 0: na = "No System(s) Selected" ; enabled = False

            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_sliders_is_open else ">   "+na
            ixon = "MOD_HUE_SATURATION"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_sliders_is_open else "DISCLOSURE_TRI_RIGHT"
     
            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_sliders_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_sliders_is_open:

                colset=layout.column()
                colset.scale_y = 0.95

                if enabled == False: colset.enabled = False
                
                colset.separator() #there's a way to tweak each .scaly_x, maybe overkill and useless. could do some cleanups. 
                colse=colset.box()
                colse.label(text="Display:")
                colserow=colse.row(align=True)
                colserow.prop(addon_prefs, "batch_dis",text="display %",slider=True)
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_dis.bl_idname, text="batch")
                colserowb.scale_x = 0.3
     
                colset.separator()
                colse=colset.box()
                colse.label(text="Particles:")

     
                emiscolumn = colse.column(align=True)
                #colse.separator(factor=0.5)
                colsebit = emiscolumn.row(align=True)
                colsebit.prop(addon_prefs,"persquaremorkm", expand=True)
                colsebit.operator(SCATTER_OT_how_much2.bl_idname,text="",icon="OUTLINER_OB_LIGHT")
                colserow=emiscolumn.row(align=True)


                colserow.prop(addon_prefs, "persquarem",text="emission Density per  " + addon_prefs.persquaremorkm)
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_emisquare.bl_idname, text="batch")
                colserowb.scale_x = 0.3
                #colse.separator(factor=0.5)
                colserow=emiscolumn.row(align=True)
                colserow.prop(addon_prefs, "batch_emi",text="emission number")
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_emi.bl_idname, text="batch")
                colserowb.scale_x = 0.3
     
                colserow=emiscolumn.row(align=True)
                colserow.prop(addon_prefs, "batch_seed",text="seed value")
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_seed_random.bl_idname, text="randomize")
                colserowb.operator(SCATTER_OT_slider_batch_seed.bl_idname, text="batch")
                colserowb.scale_x = 0.43
                 
                colse.label(text="Transformation:")

                colwcol = colse.row(align=True)
                colwcol1 = colwcol.column(align=True)
                colwcol2 = colwcol.column(align=True)
                colwcol2.scale_x = 0.955
                colwcol1.prop(addon_prefs, "batch_r_scale",text="random scale",slider=True)
                colwcol1.prop(addon_prefs, "batch_r_rot",text="random rotation",slider=True)
                colwcol1.prop(addon_prefs, "batch_r_rot_tot",text="random rotation",slider=True)
                row1 = colwcol1.row(align=True)
                ap = row1.operator(SCATTER_OT_particles_orientation.bl_idname, text="Zglobal") ; ap.option = "GLOB_Z" 
                bp = row1.operator(SCATTER_OT_particles_orientation.bl_idname, text="Hair")    ; bp.option = "VEL"
                cp = row1.operator(SCATTER_OT_particles_orientation.bl_idname, text="Znormal") ; cp.option = "NOR"
                colwcol2.operator(SCATTER_OT_slider_batch_r_scale.bl_idname, text="batch")
                colwcol2.operator(SCATTER_OT_slider_batch_r_rot.bl_idname, text="batch")
                colwcol2.operator(SCATTER_OT_slider_batch_r_rot_tot.bl_idname, text="batch")
                dp = colwcol2.operator(SCATTER_OT_particles_orientation.bl_idname, text="Zlocal")  ; dp.option = "OB_Z"

                colset.separator()
                colse=colset.box()
                colse.label(text="Texture:")
                
                colcolcol = colse.column(align=True)
                colserow=colcolcol.row(align=True)
                colserow.prop(addon_prefs, "batch_t_idens",text="density influence",slider=True)
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_t_idens.bl_idname, text="batch")
                colserowb.scale_x = 0.3
                
                colserow=colcolcol.row(align=True)
                colserow.prop(addon_prefs, "batch_t_iscal",text="scale influence",slider=True)
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_t_iscal.bl_idname, text="batch")
                colserowb.scale_x = 0.3
                                
                colcolcol = colse.column(align=True)
                colserow=colcolcol.row(align=True)
                colserow.prop(addon_prefs, "batch_t_brigh",text="color brightness",slider=True)
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_t_brigh_ran.bl_idname, text="randomize")
                colserowb.operator(SCATTER_OT_slider_batch_t_brigh.bl_idname, text="batch")
                colserowb.scale_x = 0.43
                
                colserow=colcolcol.row(align=True)
                colserow.prop(addon_prefs, "batch_t_contr",text="color contrast",slider=True)
                colserowb=colserow.row(align=True)
                colserowb.operator(SCATTER_OT_slider_batch_t_contr_ran.bl_idname, text="randomize")
                colserowb.operator(SCATTER_OT_slider_batch_t_contr.bl_idname, text="batch")
                colserowb.scale_x = 0.43
     
                colrow = colse.split()
                colrow1=colrow.column(align=True)
                colrow2=colrow.column(align=True)
                colrow1.label(text="Texture Scale:")
                colrow1.prop(addon_prefs,"batch_t_scal",text="XYZ")
                colrow1.operator(SCATTER_OT_slider_batch_t_scal_ran.bl_idname, text="randomize")
                colrow1.operator(SCATTER_OT_slider_batch_t_scal.bl_idname, text="batch")
                colrow2.label(text="Texture Offset:")
                colrow2.prop(addon_prefs,"batch_t_off",text="XYZ")
                colrow2.operator(SCATTER_OT_slider_batch_t_off_ran.bl_idname, text="randomize")
                colrow2.operator(SCATTER_OT_slider_batch_t_off.bl_idname, text="batch")       
        else:
            ixon = "MOD_HUE_SATURATION"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##

       ######################################################### PARTICLES COLLECTION
       ######################################################### PARTICLES COLLECTION
       ######################################################### PARTICLES COLLECTION


        if is_1_num == 1:
            na = "Particles Collection" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_sliders_ob_is_open else ">   "+na
            ixon = "OUTLINER_OB_GROUP_INSTANCE"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_sliders_ob_is_open else "DISCLOSURE_TRI_RIGHT"
 
            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_sliders_ob_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_sliders_ob_is_open:

                # coll_is_1 =0
                # for p in A.particle_systems:
                #     if "SCATTER" in p.name:
                #         if bpy.data.particles[p.name]["is_selected"]==1:
                #             coll_is_1 +=1
                #             particles_sys = p

                particles_sys = bpy.data.particles[is_activ]

                is_there_prox = False
                is_there_prox_error = False
                colsetro=layout.box().column(align=True)

                colsetro.box().label(text=particles_sys.name,icon='GROUP')
                colsetro.separator(factor=1.5)
                terrain_coll_name = "SCATTER: ["+A.name+"]"+" Particles"
                boxy = colsetro.box()
                for coll_child in bpy.data.collections[terrain_coll_name].children:
                    if coll_child.name == particles_sys.name: #ob
                        prox_list = []
                        for obj in bpy.data.collections[coll_child.name].objects:

                            if "[proxy]" in obj.name:
                                is_there_prox = True

                            if "[proxy]" not in obj.name:
                                if obj.name+ " [proxy]" in bpy.data.collections[coll_child.name].objects:
                                    namee = obj.name+ " + [proxy]"
                                    iconn = "SHADING_BBOX"
                                    prox_list.append(obj.name+ " [proxy]")
                                else:
                                    namee = obj.name
                                    if is_there_prox == False: iconn = "PARTICLE_DATA"
                                    else: iconn = "ERROR" ; is_there_prox_error = True
                                colsetroww=boxy.row(align=False)
                                colsetroww.label(text=namee,icon=iconn)
                                if obj.display_type == 'TEXTURED': iconb = 'MONKEY'
                                else: iconb = 'CUBE'

                                colsetroww.operator(SCATTER_OT_slider_is_bounds.bl_idname,text="",icon=iconb).part_ob_name = obj.name
                                colsetroww.operator(SCATTER_OT_collremove.bl_idname,text="",icon="REMOVE").obj_na = obj.name
                                
                        for obj in bpy.data.collections[coll_child.name].objects:
                            if "[proxy]" in obj.name:
                                if obj.name not in prox_list:
                                    is_there_prox_error = True
                                    colsetroww=boxy.row(align=False)
                                    colsetroww.label(text=obj.name,icon="ERROR")
                                    colsetroww.operator(SCATTER_OT_collremove.bl_idname,text="",icon="REMOVE").obj_na = obj.name

                colsetroww=boxy.row(align=False) ; colsetroww1 = colsetroww.row() ; colsetroww1.scale_y = 0.91
                colsetroww1.prop(C_Slots, "eye_dropper_prop",text="")
                colsetroww.operator(SCATTER_OT_colladd.bl_idname,text="",icon="ADD")
                colsetroww.operator(SCATTER_OT_selection_to_coll.bl_idname,text="",icon="SELECT_SET").coll_name = particles_sys.name
                if (is_there_prox == True and is_there_prox_error == False):
                    colsetro.separator(factor=1.0)
                    coletroww = colsetro.row()
                    #coletroww.label(text="Update of proxy system needed on any changes",icon="QUESTION")
                    coletroww.operator(SCATTER_OT_set_up_proxy.bl_idname, text="Update Proxies",icon="OBJECT_HIDDEN")
                if is_there_prox_error == True: colsetro.label(text="each assets need their own proxies",icon="ERROR")
 
        else:
            ixon = "OUTLINER_OB_GROUP_INSTANCE"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##



        ######################################################### PROXY
        ######################################################### PROXY
        ######################################################### PROXY

        if is_1_num != 1:
            ixon = "OBJECT_HIDDEN"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##

        elif is_1_num == 1:
            na = "Proxies" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_proxy_is_open else ">   "+na
            ixon = "OBJECT_HIDDEN"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_proxy_is_open else "DISCLOSURE_TRI_RIGHT"

            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_proxy_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_proxy_is_open:
                colsetrow=layout.box().column(align=False)

                particles_sys = bpy.data.particles[is_activ]

                colsetro=colsetrow.box()
                colsetro.scale_y = 1.2
                colsetro.operator(SCATTER_OT_set_up_proxy.bl_idname, text="Set-Up / Update Proxies",icon="OBJECT_HIDDEN")
                if bpy.data.particles[particles_sys.name]["is_proxy"]!='Not Yet':
                    colsetro.operator(SCATTER_OT_toggle_proxy.bl_idname, text="Toggle Proxies",icon='MONKEY'if bpy.data.particles[particles_sys.name]["is_proxy"]==0 else 'SHADING_BBOX')
                    colsetro.operator(SCATTER_OT_toggle_proxy_all.bl_idname, text="Toggle Proxies whole scene",icon='SCENE_DATA')

                    if 'is_timer_on' in bpy.context.scene:
                        if bpy.context.scene['is_timer_on']=='OFF': texxxt='Auto-Toggle on Rendered View' ; icccon="PLAY"
                        else: texxxt='Stop listening'  ; icccon="CANCEL"
                        colsetrobox = colsetro.row(align=True)
                        colsetrobox.operator(SCATTER_OT_listen_to_view.bl_idname, text=texxxt,  icon=icccon)
                        colsetrobox.prop(addon_prefs,'scatter_always_hund', text='',icon='FILE_IMAGE'if addon_prefs.scatter_always_hund is True else 'SEQ_PREVIEW')

                slid=colsetrow.row(align=False) ; slid.alignment = 'LEFT'
                slid.prop(addon_prefs,'scatter_proxy_inception_is_open',text="How to set up a proxy system:",emboss=False,icon="QUESTION")
                if addon_prefs.scatter_proxy_inception_is_open:
                    colstetroinstruction = colsetrow.box()
                    colstetroinstruction.box().label(text='Each Highpoly assets need a proxy equivalent in order to work !',icon="ERROR")
                    colstetroinstruction.label(text='1) Create a low res asset and rename him as "HighResName [proxy]"')
                    colstetroinstruction.label(text='2) add the proxy in the scattered assets list, icon and name will change')
                    colstetroinstruction.label(text='3) "Set-Up Proxies"')
                    colstetroinstruction.label(text='(or just use the scatter operator with proxies in your selection)')
                    colstetroinstruction.scale_y = 0.85







        ######################################################### POINT CLOUD
        ######################################################### POINT CLOUD
        ######################################################### POINT CLOUD

        if is_1_num >= 1:
            na = "Point Cloud" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_is_cloud else ">   "+na
            ixon = "LIGHTPROBE_GRID"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_is_cloud else "DISCLOSURE_TRI_RIGHT"

            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_is_cloud',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_is_cloud:
                colsetrow=layout.box().column(align=False)
                colsetrow.label(text="on construction",icon="EXPERIMENTAL")

        else:
            ixon = "LIGHTPROBE_GRID"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##







        ######################################################### CAMERA
        ######################################################### CAMERA
        ######################################################### CAMERA
               
        if is_1_num >= 0:
            na = "Camera Clipping" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_camera_is_open else ">   "+na
            ixon = "CAMERA_DATA"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_camera_is_open else "DISCLOSURE_TRI_RIGHT"
        
            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_camera_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_camera_is_open:

                colsetrow=layout.box().column(align=False)
                colsetro=colsetrow.box().column(align=False)
                colsetro.operator(SCATTER_OT_camera_crop_and_density.bl_idname, text="Set-Up Clipping", icon="CAMERA_DATA")
                colsetro.scale_y = 1.2
                Show_del = False
                for m in A.modifiers:
                    if "CAM" in m.name: Show_del = True
                if Show_del == True:
                    colsetro.separator(factor=0.7)
                    colsetro.operator(SCATTER_OT_delete_cam.bl_idname, text="Remove Clipping", icon="PANEL_CLOSE")
                    colsetrow.separator(factor=1.3)
        
                    for p in A.particle_systems:
                        if "SCATTER:" in p.name:
                            colsetrowROW = colsetrow.row(align=False)
                            colsetrowROW.label(text=p.name[9:])
                            if "CAM-DEN: "+p.name[9:] in A.modifiers:
                                colsetrowROW.operator(SCATTER_OT_toggle_dens.bl_idname, text="", icon="MOD_VERTEX_WEIGHT" if A.modifiers["CAM-DEN: "+p.name[9:]].show_viewport == 1 else "BLANK1").psys = p.name
                                colsetrowROW.operator(SCATTER_OT_toggle_clip.bl_idname, text="", icon="CAMERA_DATA" if A.modifiers["CAM-CUT: "+p.name[9:]].show_viewport == 1 else "BLANK1").psys = p.name
                                colsespace = colsetrowROW.row(); colsespace.scale_x = 0.3; colsespace.label(text="",icon="BLANK1")
                            else:
                                colsetrowRR = colsetrowROW.row()# ; colsetrowRR.scale_x = 0.5
                                colsetrowRR.operator(SCATTER_OT_camera_crop_and_density.bl_idname, text="Update")#, icon="OUTLINER_OB_CAMERA")
                                colsespace = colsetrowROW.row(); colsespace.scale_x = 0.3; colsespace.label(text="",icon="BLANK1")
                    if "CAM-DEN: Camera-Dens" in A.modifiers:
                        colsetrow.separator(factor=0.5)
                        colseslide = colsetrow.row(align=False)
                        colseslide.label(text="",icon="BLANK1")
                        colseslide.prop(A.modifiers["CAM-DEN: Camera-Dens"],"min_dist",text="distance culling",slider=True, icon="SEQ_LUMA_WAVEFORM") #"CAM-DEN: "+p.name[9:]
                        colseslide.label(text="",icon="BLANK1")
                        colseslide.scale_x = 0.03
        
                        colsetrow.separator(factor=0.5)
                        colseslide = colsetrow.row(align=False)
                        colseslide.label(text="",icon="BLANK1")
                        colseslide.prop(A.modifiers["CAM-DEN: Camera-Dens"],"mask_constant",text="influence",slider=True, icon="ONIONSKIN_ON") #"CAM-DEN: "+p.name[9:]
                        colseslide.label(text="",icon="BLANK1")
                        colseslide.scale_x = 0.03
        
                    colsetrow.separator(factor=1.3)
                    colsetrorefresh = colsetrow.box().column() ; colsetrorefresh.scale_y =1.2
                    colsetrorefresh.operator(SCATTER_OT_refresh.bl_idname, text="Refresh Terrain",icon='FILE_REFRESH')
                    colsetrorefresh.separator(factor=0.7)
                    terr = A.name
                    if "refresh_watch" in A:
                        if A["refresh_watch"]==True: icox = 'CANCEL'
                        else: icox = 'PLAY'
                    else: icox = 'PLAY'
                    colsetrorefresh.operator(SCATTER_OT_auto_toggle.bl_idname, text="Auto-Terrain Refresh on Camera move",icon=icox)
        
                    colsetrow.separator(factor=0.6)
                    check_box = colsetrow.column() ; check_box.scale_y = 0.9
                    check_box.prop(addon_prefs,'scatter_is_cam_zone',text="enable camera clipping threshold")
                    if addon_prefs.scatter_is_cam_zone == True:
                        colsetrow.separator(factor=0.75)
                        colsetrowROW = colsetrow.box().column(align=False)
                        colsetrowROW.scale_y = 0.8
                        colsetrowROW.prop(bpy.data.objects["CAM-CUT: Camera-Clip"],"scale",text="Camera Clipping XYZ Threshold")

        else:
            ixon = "CAMERA_DATA"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##







        ######################################################### PAINTING
        ######################################################### PAINTING
        ######################################################### PAINTING
        
        if is_1_num >= 0:
            na = "Painting" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_is_paint else ">   "+na
            ixon = "WPAINT_HLT"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_is_paint else "DISCLOSURE_TRI_RIGHT"
        
            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_is_paint',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_is_paint:
                box=layout.box()
        
                colse=box.box().column(align=False)
                colse.scale_y=1.2
                colse.operator(SCATTER_OT_paint.bl_idname, text="New Paint Layer",icon="WPAINT_HLT")
        
                have_some = False
                for v in A.vertex_groups:
                    if "PAINT" in v.name:
                        singlebox = box.box()
                        colsetile = singlebox.box()
                        colserow  = colsetile.row(align=False)
                        colserow.label(icon="GROUP_VERTEX")
                        colserow.prop(bpy.context.scene, '["'+v.name+'"]',text="")
                        colserow.operator(SCATTER_OT_paint_go_in_weight.bl_idname, text="",icon="BRUSH_DATA").paint_layer = v.name
                        colserow.operator(SCATTER_OT_paint_clear.bl_idname, text="",icon="TRASH").paint_layer = v.name
                        colserow.operator(SCATTER_OT_paint_invert.bl_idname, text="",icon="UV_SYNC_SELECT").paint_layer = v.name
                        colserow.operator(SCATTER_OT_paint_del.bl_idname, text="",icon="PANEL_CLOSE").paint_layer = v.name
                        for m in A.modifiers:
                            if v.name in m.name:
                                colserow = singlebox.row(align=False)
                                colserow.operator(SCATTER_OT_inverseinfluence.bl_idname, text="",icon='ARROW_LEFTRIGHT' if A.modifiers["INVERT:"+m.vertex_group_a[9:]].show_viewport ==True else "BLANK1" ).of_this_one = m.vertex_group_a[9:]
                                colserow.label(text=m.vertex_group_a[9:])
                                #colserow.label(text="",icon="RESTRICT_VIEW_OFF" if m.show_render == True else "RESTRICT_VIEW_ON")
                                colserow.operator(SCATTER_OT_add_remove.bl_idname, text="",icon='SELECT_INTERSECT' if m.mix_mode == 'ADD' else 'SELECT_DIFFERENCE').concerned_m = m.name
                                colserow.operator(SCATTER_OT_paint_show.bl_idname, text="",icon="RESTRICT_VIEW_OFF" if m.show_render == True else "RESTRICT_VIEW_ON").concerned_m = m.name
                                colserow.operator(SCATTER_OT_paint_infl_rem.bl_idname, text="",icon="REMOVE").concerned_m = m.name
                        add = singlebox.column() ; add.scale_y = 0.85
                        add.operator(SCATTER_OT_paint_part_infl.bl_idname, text="Add Influence to Selected System(s)",icon="ADD").paint_layer = v.name
                        have_some = True
        
                if  have_some == True:
                    slid=box.row(align=True)
                    slid.alignment = 'LEFT'
                    slid.prop(addon_prefs,'scatter_is_paint_q',text="Info: Paint layers only can ADD weight",emboss=False,icon="QUESTION")
                    if addon_prefs.scatter_is_paint_q:
                        text=box.box()
                        text.box().label(text="paint layers will only ADD weight to the current distribution",icon="ERROR")
                        space = text.column() ; space.label(text="") ; space.scale_y = -0.5
                        text.label(text="you may want to invert the vgroup with the 'invert system vgroup'")
                        space = text.column() ; space.label(text="") ; space.scale_y = -0.7
                        text.label(text="operator first (next to the display button) to see a result of your weight painting.")
                        space = text.column() ; space.label(text="") ; space.scale_y = -0.7
                        text.box().label(text="booleans aren't allowed to remove any weight from your painting vgroup",icon="SELECT_SUBTRACT")
        else:
            ixon = "WPAINT_HLT"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##
                       

                           






        ######################################################### BOOLEAN
        ######################################################### BOOLEAN
        ######################################################### BOOLEAN
        
        if is_1_num >= 0:
            na = "Boolean" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_sliders_curv_is_open else ">   "+na
            ixon = "SELECT_SUBTRACT"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_sliders_curv_is_open else "DISCLOSURE_TRI_RIGHT"
        
            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_sliders_curv_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_sliders_curv_is_open:
                have_some = False
                curvebox=layout.box().column()
                curveboxop=curvebox.box().column() ; curveboxop.scale_y=1.2
                curveboxop.operator(SCATTER_OT_Bool_Path.bl_idname, text="New Boolean(s) on Selected system(s)",icon='SELECT_SUBTRACT')
                curvebox.separator(factor=0.3)
        
                for c in bpy.context.scene.objects:
                    if c.type == "CURVE":
                        if "tab_open" in bpy.data.objects[c.name]:
                            mod = [mod for mod in A.modifiers if "["+c.name+"]" in mod.name]
        
                            sel = bpy.context.selected_objects
                            curvebox.separator(factor=0.75)
                            lilbx = curvebox.box()
                            title = lilbx.box().row()
                            title.label(text=c.name,icon="OUTLINER_OB_CURVE")
                            #title.operator(SCATTER_OT_bool_open_min_tab.bl_idname, text="",icon='BLENDER').cuname = c.name #meh,with button= ugly
                            title.operator(SCATTER_OT_activeisname.bl_idname, text="",icon='RESTRICT_SELECT_OFF' if c in sel else 'RESTRICT_SELECT_ON').futureactivename = c.name
                            title.operator(SCATTER_OT_hidecurve.bl_idname, text="",icon='HIDE_OFF').tobehidden = c.name
                            title.operator(SCATTER_OT_destroycurve.bl_idname, text="",icon='PANEL_CLOSE').futureactivename = c.name
    
                            if bpy.data.objects[c.name]["tab_open"] == True:
                                for m in mod:
                                    lilrow = lilbx.row()
                                    lilrow.operator(SCATTER_OT_inverseinfluence.bl_idname, text="",icon='ARROW_LEFTRIGHT' if A.modifiers["INVERT:"+m.name[7+len(c.name):]].show_viewport ==True else "BLANK1" ).of_this_one = m.name[7+len(c.name):]
                                    lilrow.label(text=m.name[7+len(c.name):])
                                    allmod = [mod for mod in A.modifiers]; 
                                    lilrow.operator(SCATTER_OT_paint_show.bl_idname, text="",icon="RESTRICT_VIEW_OFF" if m.show_viewport == True else "RESTRICT_VIEW_ON").concerned_m = m.name
                                    lilrow.operator(SCATTER_OT_paint_infl_rem.bl_idname, text="",icon="REMOVE").concerned_m = m.name
                                add = lilbx.column() ; add.scale_y = 0.85
                                add.operator(SCATTER_OT_bool_add_inlfe.bl_idname, text="Add Influence to Selected System(s)",icon='ADD').curve_na = c.name
                            have_some = True
        
                if have_some == True:
                    curvebox.separator(factor=0.75)
                    refresh = curvebox.box() ; refresh.scale_y =1.2
                    refresh.operator(SCATTER_OT_refresh.bl_idname, text="Refresh Terrain",icon='FILE_REFRESH')
       
                curvebox.separator(factor=0.4)
        else:
            ixon = "SELECT_SUBTRACT"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4##

        ######################################################### BOOLEAN BEZIER
        ######################################################### BOOLEAN BEZIER
        ######################################################### BOOLEAN BEZIER

        if A:
            na = "Boolean Tweaking" 
            if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_sliders_curv_adv_is_open else ">   "+na
            ixon = "CURVE_DATA"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_sliders_curv_adv_is_open else "DISCLOSURE_TRI_RIGHT"

            slid=layout.row(align=True) ; slid.scale_y = 1.4##
            slid.alignment = 'LEFT'
            slid.prop(addon_prefs,'scatter_sliders_curv_adv_is_open',text=na,emboss=False,icon=ixon)
            if addon_prefs.scatter_sliders_curv_adv_is_open:

                display = False
                curcount = 0

                for cur in bpy.context.selected_objects:
                    if cur.type == 'CURVE':
                        curcount +=1
                        cur = cur
                        curvename = cur.name

                curvebox=layout.column()
                boxception = curvebox.box()
                boxtitle = boxception.box().row()

                if curcount !=0:
                    if A.type == 'MESH':
                        for m in A.modifiers:
                            if 'BOOL' in m.name:
                                if m.name[5:len(cur.name)+7] == "["+cur.name+"]":
                                    display = True
                    elif A.type == 'CURVE':
                        if A.parent:
                            for m in A.parent.modifiers:
                                if 'BOOL' in m.name:
                                    if m.name[5:len(cur.name)+7] == "["+cur.name+"]":
                                        display = True

                if curcount==1: boxtitle.label(text='Tweak "'+curvename+'"')
                elif curcount>1:  boxtitle.label(text='Batch Tweak Multiples Curves')
                elif curcount==0:  boxtitle.label(text='Select A Boolean')

                boxception.prop(addon_prefs,"batch_curve_dist",text="radius [m]/each sides")
                boxception.prop(addon_prefs,"batch_curve_falloff",text="falloff [m]")
                boxception.prop(addon_prefs,"batch_curve_infl",text="influence",slider=True)
                boxdisable = boxception.row()
                op = boxdisable.operator(SCATTER_OT_curvesliderinfluence.bl_idname,text="apply")
                if curcount != 0: op.curvenamee = cur.name
                else: boxdisable.enabled = False
        if not A:
            ixon = "CURVE_DATA"
            if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_RIGHT"
            slid=layout.row(align=True) ; slid.label(text=nam,icon=ixon) ; slid.scale_y = 1.4

#
#
#
#
#        ######################################################### PERF WARNING
#        ######################################################### PERF WARNING
#        ######################################################### PERF WARNING 
#
#        na = "About Performances" 
#        if addon_prefs.scatter_ui_is_tri == False:  na = "V   "+na if addon_prefs.scatter_is_warning else ">   "+na
#        ixon = "QUESTION"
#        if addon_prefs.scatter_ui_is_tri == True: ixon = "DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_is_warning else "DISCLOSURE_TRI_RIGHT"
#
#        slid=layout.row(align=True) ;
#        slid.alignment = 'LEF ; slid.scale_y = 1.25#T'
#        slid.prop(addon_prefs,'scatter_is_warning',text=na,emboss=False,icon=ixon)
#        if addon_prefs.scatter_is_warning:
#            curvebox=layout.column()
#            boxx = curvebox.box()
#            boxx.label(text="Scatter is an automation system, native blender performances issues are still present")
#            space = boxx.column() ; space.label(text=" ") ; space.scale_y = -0.75
#            boxx.label(text="Here's a guide on how to manage your computer perfs when working on particles:")
#            


######################################################################################
#
#ooooooooo.   ooooooooooooo      ooooooooooooo                     oooo
#`888   `Y88. 8'   888   `8      8'   888   `8                     `888
# 888   .d88'      888                888       .ooooo.   .ooooo.   888   .oooo.o
# 888ooo88P'       888                888      d88' `88b d88' `88b  888  d88(  "8
# 888              888                888      888   888 888   888  888  `"Y88b.
# 888              888                888      888   888 888   888  888  o.  )88b
#o888o            o888o              o888o     `Y8bod8P' `Y8bod8P' o888o 8""888P'
#
######################################################################################


class SCATTER_PT_Tools(bpy.types.Panel):
    bl_idname = "SCATTER_PT_Tools"
    bl_label = "Tools"
    bl_category = "Scatter BETA"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"

    def draw(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = bpy.context.object
        layout = self.layout

        box=layout.box() ; button = box.column() ; button.scale_y=1.2
        if C_Slots.Terrain_pointer ==None: button.enabled =False
        button.operator(SCATTER_OT_refresh.bl_idname, text="Refresh Terrain",icon='FILE_REFRESH')

        box=layout.box() ; button = box.column() ; button.scale_y=1.2
        button.operator(SCATTER_OT_quick_turn.bl_idname, text="Particles 90° Turn(s)",icon='CON_FOLLOWPATH')

        box=layout.box() ; button = box.column() ; button.scale_y=1.2
        button.operator(SCATTER_OT_low_origin.bl_idname, text="Particles Low Origin",icon='SORT_ASC')

        box=layout.box() ; button = box.column() ; button.scale_y=1.2
        button.operator(SCATTER_OT_is_proxy_of_active.bl_idname, text="Crearte Proxy Name of Active",icon='FONTPREVIEW')

        box=layout.box() ; button = box.column() ; button.scale_y=1.2
        button.operator(SCATTER_OT_particle_optimizer.bl_idname, text="Particles Viewport Optimizer",icon='MOD_DECIM')
        button = box.row(align=False)
        button.prop(addon_prefs,"particle_optimizer",text="Optimization %",slider=True)
        if A:
            if "Particle optimisation" in A.modifiers:
                button.prop(A.modifiers["Particle optimisation"],"show_viewport",text='',icon='RESTRICT_VIEW_ON')
                button.operator(SCATTER_OT_particle_optimizer_remover.bl_idname, text="",icon='PANEL_CLOSE')
        button.scale_y=0.7

        box=layout.box() ; button = box.row(align=True) ; button.scale_y=1.2
        button.operator(SCATTER_OT_disp_small.bl_idname, text="Noise 1",icon='MOD_DISPLACE')
        button.operator(SCATTER_OT_disp_big.bl_idname, text="Noise 2")
        i=0

        if A:
            for m in A.modifiers:
                if m.type=='DISPLACE':
                    button = box.column()
                    i+=1
                    if i==1:
                        row = button.row(align=False)
                        row.alignment = 'LEFT'
                        row.prop(addon_prefs,'scatter_nois_is_open',text="Terrain Noise Parameters              ",emboss=False,icon="DISCLOSURE_TRI_DOWN" if addon_prefs.scatter_nois_is_open else "DISCLOSURE_TRI_RIGHT")
                        row = row.row(align=True)
                        row.alignment = 'RIGHT'
                        row.operator(SCATTER_OT_remove_apply.bl_idname, text="", icon='PANEL_CLOSE').is_apply=False
                        row.operator(SCATTER_OT_remove_apply.bl_idname, text="", icon='IMPORT').is_apply=True
                        row.scale_y = 0.9
                    if addon_prefs.scatter_nois_is_open==True:
                        if "SCATTER: Noise Displace (Small)" in m.name:
                            button.label(text='Noise 1')

                            button.prop(A.modifiers["SCATTER: Noise Displace (Small)"],"strength",text='modifier strength')

                            button.prop(bpy.data.textures["SCATTER: Noise Displace (Small)"],"noise_scale")
                        space=button.column()
                        space.scale_y=0.2
                        space.label(text="")
                        if "SCATTER: Noise Displace (Big)" in m.name:
                            button.label(text='Noise 2')

                            button.prop(A.modifiers["SCATTER: Noise Displace (Big)"],"strength",text='modifier strength')

                            button.prop(bpy.data.textures["SCATTER: Noise Displace (Big)"],"noise_scale")

        box=layout.box() ; button = box.column() ; button.scale_y=1.2
        button.operator(SCATTER_OT_import_proxies.bl_idname, text="Load basic Proxies Mesh",icon='SELECT_SET')
















######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
#       
#       ooooooooo.                                             .
#       `888   `Y88.                                         .o8
#        888   .d88' oooo d8b  .ooooo.   .oooo.o  .ooooo.  .o888oo  .oooo.o
#        888ooo88P'  `888""8P d88' `88b d88(  "8 d88' `88b   888   d88(  "8
#        888          888     888ooo888 `"Y88b.  888ooo888   888   `"Y88b.
#        888          888     888    .o o.  )88b 888    .o   888 . o.  )88b
#       o888o        d888b    `Y8bod8P' 8""888P' `Y8bod8P'   "888" 8""888P'
#                                                                                                                                
######################################################################################




class SCATTER_OT_C_Slots_Settings(bpy.types.PropertyGroup):
    C_name                : StringProperty(name="Preset Name",subtype='NONE',default="Simple")
    C_is_fur              : BoolProperty(name="is fur",subtype='NONE',default=False)
    C_is_else             : BoolProperty(name="is else",subtype='NONE',default=False)

    C_desc                : StringProperty(name="Preset Descrition",subtype='NONE',default='Random Scattering, 10p/m², no textures')
    C_per_vert            : BoolProperty(name="Emit one Particle per verticles",subtype='NONE',default=False)
    C_per_face            : BoolProperty(name="Emit one Particle per faces",subtype='NONE',default=False)
    C_count               : IntProperty(name="Emission Number",subtype='NONE',default=1000,min=0)
    C_countispersquare    : EnumProperty(name="Emission Number is per square",description=' ',items =[('None','None','','BLANK1',1),('/m²','/m²','','BLANK1',2),('/km²','/km²','','BLANK1',3),],default='/m²')
    C_countpersquare      : IntProperty(name="Emission Number per square",subtype='NONE',default=10,min=0)
    C_seed                : IntProperty(name="Emission Seed Value",subtype='NONE',default=5,min=0)
    C_seed_is_random      : BoolProperty(name="Emission Random Seed Value",subtype='NONE',default=True)
    C_particle_size       : FloatProperty(name="Render Scale (Default = True size) ",subtype='NONE',default=1,min=0.01,max=3)
    C_size_random         : FloatProperty(name="Render Scale Randomness",subtype='NONE',default=0.35,min=0,max=1)
    C_phase_factor_random : FloatProperty(name="Rotation Randomize Phase",subtype='NONE',default=2,min=0,max=2)
    C_orientation         : EnumProperty(name='Particles orientation',description='Particles orientation',items =[('GlobalZ','Z global','',1),('Haiz','Hair Velocity','',2),('NormalZ','Z normal','',3),('LocalZ','Z Local','',4)],default='GlobalZ')
    C_phase_rotation      : FloatProperty(name="Rotation Randomize",subtype='NONE',default=0.015,min=0,max=1)

    C_use_children        : BoolProperty(name="Use Interpolated Children (may cause too much particles for your computer to handle)",subtype='NONE',default=False)
    C_children_ammount    : IntProperty(name="Children Ammount",subtype='NONE',default=10,min=0,max=100)
    C_children_roughness  : FloatProperty(name="Children Roughness uniform (texture intensity)",subtype='NONE',default=0,min=0,max=20)
    C_children_roughness_s: FloatProperty(name="Children Roughness scale (texture scaling)",subtype='NONE',default=1,min=0.01,max=10000)
    C_children_clump      : FloatProperty(name="Children Clumping (group uniformisation)",subtype='NONE',default=0,min=-1,max=1)
    
    C_texture_type        : EnumProperty(name='Texture Type',description='Texture Clustering Type',items =[('Automatic','Procedural','','NODETREE',1),('Texture','Texture','','FILE_IMAGE',2),('None','None','','PANEL_CLOSE',3),],default='None')
    
    C_noise_scale         : FloatProperty(name="Texture Noise Size",subtype='NONE',default=1.5,min=0.01,max=100)
    C_noise_scaleisrandom : BoolProperty(name="Texture Noise Size Random Values",subtype='NONE',default=False)
    C_noise_scaleA        : FloatProperty(name="Texture Noise Size Possibilities Range From A",subtype='NONE',default=0.75,min=0.01,max=100)
    C_noise_scaleB        : FloatProperty(name="To B",subtype='NONE',default=2.3,min=0.01,max=100)
    C_noise_randomtext    : BoolProperty(name="Texture Color Contrast/Brightness Randomisation",subtype='NONE',default=False)
    C_noise_depth         : IntProperty(name="Texture Noise Depth",subtype='NONE',default=0,min=0,max=20)
    C_contrast            : FloatProperty(name="Texture Color Contrast",subtype='NONE',default=3,min=0,max=5)
    C_intensity           : FloatProperty(name="Texture Color Brightness",subtype='NONE',default=1,min=0,max=2)
    C_density_factor      : FloatProperty(name="Texture Influence Density",subtype='NONE',default=1,min=0,max=1)
    C_length_factor       : FloatProperty(name="Texture Influence Scale",subtype='NONE',default=0.3,min=0,max=1)
    C_scalex              : FloatProperty(name="Texture Mapping size X",subtype='NONE',default=1,min=-100,max=100)
    C_scaley              : FloatProperty(name="Texture Mapping size Y",subtype='NONE',default=1,min=-100,max=100)
    C_scalez              : FloatProperty(name="Texture Mapping size Z",subtype='NONE',default=1,min=-100,max=100)
    C_offsetx             : FloatProperty(name="Texture Mapping offset X in meters",subtype='NONE',default=0,min=-100,max=100)
    C_offsety             : FloatProperty(name="Texture Mapping offset Y in meters",subtype='NONE',default=0,min=-100,max=100)
    C_offsetz             : FloatProperty(name="Texture Mapping offset Z in meters",subtype='NONE',default=0,min=-100,max=100)
    C_size_is_random      : BoolProperty(name="Texture Mapping Random Size Value XYZ",subtype='NONE',default=False)
    C_size_A              : FloatProperty(name="Size Possibilities Range From A",subtype='NONE',default=0.7,min=-100,max=100)
    C_size_B              : FloatProperty(name="To B",subtype='NONE',default=1.4,min=-100,max=100)
    C_offset_is_random    : BoolProperty(name="Texture Mapping Random Offset Value XYZ in meters",subtype='NONE',default=True)
    C_offset_A            : FloatProperty(name="Offset Possibilities Range From A",subtype='NONE',default=0,min=-100,max=100)
    C_offset_B            : FloatProperty(name="To B",subtype='NONE',default=100,min=-100,max=100)
    C_use_band            : BoolProperty(name="Use Band Noise Texture Instead",subtype='NONE',default=False)
    C_band_turbulance     : FloatProperty(name="Texture Noise Turbulence",subtype='NONE',default=0,min=0,max=100)

    C_texture_or_img1     : EnumProperty(name='Texture or Image',description='Texture or Image',items =[('Image','Image','','FILE_IMAGE',1),('Texture','Texture','','TEXTURE',2),('Terrain','Terrain bake img data','','OUTLINER_DATA_LIGHTPROBE',3)],default='Image')
    C_texture_name1       : StringProperty(name="Texture Name",subtype='NONE',default="does_this_exist.jpg")
    C_texture_uv1         : BoolProperty(name="projection = UV mapping instead of Global",subtype='NONE',default=False)

    C_texture_type2       : EnumProperty(name='Texture Type',description='Texture Clustering Type',items =[('Automatic','Procedural','','NODETREE',1),('Texture','Texture','','FILE_IMAGE',2),('None','None','','PANEL_CLOSE',3),],default='None')

    C_noise_scale2        : FloatProperty(name="Texture Noise Size",subtype='NONE',default=1.5,min=0.01,max=100)
    C_noise_scaleisrandom2: BoolProperty(name="Texture Noise Size Random Values",subtype='NONE',default=False)
    C_noise_scaleA2       : FloatProperty(name="Texture Noise Size Possibilities Range From A",subtype='NONE',default=0.75,min=0.01,max=100)
    C_noise_scaleB2       : FloatProperty(name="To B",subtype='NONE',default=2.3,min=0.01,max=100)
    C_noise_randomtext2   : BoolProperty(name="Texture Color Contrast/Brightness Randomisation",subtype='NONE',default=False)
    C_noise_depth2        : IntProperty(name="Texture Noise Depth",subtype='NONE',default=0,min=0,max=20)
    C_contrast2           : FloatProperty(name="Texture Color Contrast",subtype='NONE',default=3,min=0,max=5)
    C_intensity2          : FloatProperty(name="Texture Color Brightness",subtype='NONE',default=1,min=0,max=2)
    C_density_factor2     : FloatProperty(name="Texture Influence Density",subtype='NONE',default=1,min=0,max=1)
    C_length_factor2      : FloatProperty(name="Texture Influence Length",subtype='NONE',default=0.3,min=0,max=1)
    C_scalex2             : FloatProperty(name="Texture Mapping size X",subtype='NONE',default=1,min=-100,max=100)
    C_scaley2             : FloatProperty(name="Texture Mapping size Y",subtype='NONE',default=1,min=-100,max=100)
    C_scalez2             : FloatProperty(name="Texture Mapping size Z",subtype='NONE',default=1,min=-100,max=100)
    C_offsetx2            : FloatProperty(name="Texture Mapping offset X in meters",subtype='NONE',default=0,min=-100,max=100)
    C_offsety2            : FloatProperty(name="Texture Mapping offset Y in meters",subtype='NONE',default=0,min=-100,max=100)
    C_offsetz2            : FloatProperty(name="Texture Mapping offset Z in meters",subtype='NONE',default=0,min=-100,max=100)
    C_size_is_random2     : BoolProperty(name="Texture Mapping Random Size Value XYZ",subtype='NONE',default=False)
    C_size_A2             : FloatProperty(name="Size Possibilities Range From A",subtype='NONE',default=0.7,min=-100,max=100)
    C_size_B2             : FloatProperty(name="To B",subtype='NONE',default=1.4,min=-100,max=100)
    C_offset_is_random2   : BoolProperty(name="Texture Mapping Random Offset Value XYZ in meters",subtype='NONE',default=True)
    C_offset_A2           : FloatProperty(name="Offset Possibilities Range From A",subtype='NONE',default=0,min=-100,max=100)
    C_offset_B2           : FloatProperty(name="To B",subtype='NONE',default=100,min=-100,max=100)
    C_use_band2           : BoolProperty(name="Use Band Noise Texture Instead",subtype='NONE',default=False)
    C_band_turbulance2    : FloatProperty(name="Texture Noise Turbulence",subtype='NONE',default=0,min=0,max=100)

    C_texture_or_img2     : EnumProperty(name='Texture or Image',description='Texture or Image',items =[('Image','Image','','FILE_IMAGE',1),('Texture','Texture','','TEXTURE',2),('Terrain','Terrain bake img data','','OUTLINER_DATA_LIGHTPROBE',3)],default='Image')
    C_texture_name2       : StringProperty(name="Texture Name",subtype='NONE',default="does_this_exist.jpg")
    C_texture_uv2         : BoolProperty(name="projection = UV mapping instead of Global",subtype='NONE',default=False)

    eye_dropper_prop : PointerProperty(type=bpy.types.Object) #Here because addonpref don't accept it
    Terrain_pointer  : PointerProperty(type=bpy.types.Object) #Here because addonpref don't accept it

class SCATTER_OT_C_Slots_PresetsAdd(AddPresetBase, bpy.types.Operator):
    bl_idname = 'scatter.custom_slot_preset_add_operator'
    bl_label = 'Save this setting preset to directory'
    bl_options = {'REGISTER', 'UNDO'}
    preset_menu = 'Scatter_MT_C_Slots_PresetMenu'
    preset_subdir = 'scatter_presets_custom'
    bl_description = "Will save or delete your preset"

    preset_defines = ["C_Slots = bpy.context.scene.C_Slots_settings"]
    preset_values = [
            "C_Slots.C_name",
            "C_Slots.C_is_fur",#forLater
            "C_Slots.C_is_else",#forLater

            "C_Slots.C_desc",
            "C_Slots.C_per_vert",
            "C_Slots.C_per_face",
            "C_Slots.C_count",
            "C_Slots.C_countispersquare",
            "C_Slots.C_countpersquare",
            "C_Slots.C_seed",
            "C_Slots.C_seed_is_random",
            "C_Slots.C_particle_size",
            "C_Slots.C_size_random",
            "C_Slots.C_phase_factor_random",
            "C_Slots.C_orientation",
            "C_Slots.C_phase_rotation",

            "C_Slots.C_texture_type",
            "C_Slots.C_noise_scale",
            "C_Slots.C_noise_scaleisrandom",
            "C_Slots.C_noise_scaleA",
            "C_Slots.C_noise_scaleB",
            "C_Slots.C_noise_randomtext",
            "C_Slots.C_noise_depth",
            "C_Slots.C_contrast",
            "C_Slots.C_intensity",
            "C_Slots.C_density_factor",
            "C_Slots.C_length_factor",
            "C_Slots.C_scalex",
            "C_Slots.C_scaley",
            "C_Slots.C_scalez",
            "C_Slots.C_offsetx",
            "C_Slots.C_offsety",
            "C_Slots.C_offsetz",
            "C_Slots.C_size_is_random",
            "C_Slots.C_size_A",
            "C_Slots.C_size_B",
            "C_Slots.C_offset_is_random",
            "C_Slots.C_offset_A",
            "C_Slots.C_offset_B",
            "C_Slots.C_use_band",
            "C_Slots.C_band_turbulance",

            "C_Slots.C_texture_or_img1",
            "C_Slots.C_texture_name1",
            "C_Slots.C_texture_uv1",

            "C_Slots.C_texture_type2",

            "C_Slots.C_use_children",
            "C_Slots.C_children_ammount",
            "C_Slots.C_children_roughness",
            "C_Slots.C_children_roughness_s",
            "C_Slots.C_children_clump",
            "C_Slots.C_noise_scale2",
            "C_Slots.C_noise_scaleisrandom2",
            "C_Slots.C_noise_scaleA2",
            "C_Slots.C_noise_scaleB2",
            "C_Slots.C_noise_randomtext2",
            "C_Slots.C_noise_depth2",
            "C_Slots.C_contrast2",
            "C_Slots.C_intensity2",
            "C_Slots.C_density_factor2",
            "C_Slots.C_length_factor2",
            "C_Slots.C_scalex2",
            "C_Slots.C_scaley2",
            "C_Slots.C_scalez2",
            "C_Slots.C_offsetx2",
            "C_Slots.C_offsety2",
            "C_Slots.C_offsetz2",
            "C_Slots.C_size_is_random2",
            "C_Slots.C_size_A2",
            "C_Slots.C_size_B2",
            "C_Slots.C_offset_is_random2",
            "C_Slots.C_offset_A2",
            "C_Slots.C_offset_B2",
            "C_Slots.C_use_band2",
            "C_Slots.C_band_turbulance2",

            "C_Slots.C_texture_or_img2",        
            "C_Slots.C_texture_name2",        
            "C_Slots.C_texture_uv2",            
            ]

class SCATTER_OT_C_Slots_Settings_reset(bpy.types.Operator):
    bl_idname      = "scatter.c_slots_reset"
    bl_label       = "Reset the settings"
    bl_description = ""

    def execute(self, context):
        context = bpy.context
        scene   = context.scene
        A       = context.object
        addon_prefs = context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings
        C_Slots.property_unset("C_name")
        C_Slots.property_unset("C_is_fur")#For_later
        C_Slots.property_unset("C_is_else")#For_later  
          
        C_Slots.property_unset("C_desc")
        C_Slots.property_unset("C_per_vert")
        C_Slots.property_unset("C_per_face")
        C_Slots.property_unset("C_count")
        C_Slots.property_unset("C_countispersquare")
        C_Slots.property_unset("C_countpersquare")
        C_Slots.property_unset("C_seed")                         
        C_Slots.property_unset("C_seed_is_random")
        C_Slots.property_unset("C_particle_size")
        C_Slots.property_unset("C_size_random")
        C_Slots.property_unset("C_phase_factor_random")
        C_Slots.property_unset("C_orientation")
        C_Slots.property_unset("C_phase_rotation")

        C_Slots.property_unset("C_texture_type")
        C_Slots.property_unset("C_noise_scale")
        C_Slots.property_unset("C_noise_scaleisrandom")
        C_Slots.property_unset("C_noise_scaleA")
        C_Slots.property_unset("C_noise_scaleB")
        C_Slots.property_unset("C_noise_randomtext")
        C_Slots.property_unset("C_noise_depth")
        C_Slots.property_unset("C_contrast")
        C_Slots.property_unset("C_intensity")
        C_Slots.property_unset("C_density_factor")
        C_Slots.property_unset("C_length_factor")
        C_Slots.property_unset("C_scalex")                         
        C_Slots.property_unset("C_scaley")                         
        C_Slots.property_unset("C_scalez")                         
        C_Slots.property_unset("C_offsetx")                         
        C_Slots.property_unset("C_offsety")                         
        C_Slots.property_unset("C_offsetz")                         
        C_Slots.property_unset("C_size_is_random")
        C_Slots.property_unset("C_size_A")                         
        C_Slots.property_unset("C_size_B")                         
        C_Slots.property_unset("C_offset_is_random")
        C_Slots.property_unset("C_offset_A")
        C_Slots.property_unset("C_offset_B")
        C_Slots.property_unset("C_use_band")
        C_Slots.property_unset("C_band_turbulance")

        C_Slots.property_unset("C_texture_or_img1")
        C_Slots.property_unset("C_texture_name1")
        C_Slots.property_unset("C_texture_uv1")

        C_Slots.property_unset("C_texture_type2")

        C_Slots.property_unset("C_use_children")
        C_Slots.property_unset("C_children_ammount")
        C_Slots.property_unset("C_children_roughness")
        C_Slots.property_unset("C_children_roughness_s")
        C_Slots.property_unset("C_children_clump")
        C_Slots.property_unset("C_noise_scale2")
        C_Slots.property_unset("C_noise_scaleisrandom2")
        C_Slots.property_unset("C_noise_scaleA2")
        C_Slots.property_unset("C_noise_scaleB2")
        C_Slots.property_unset("C_noise_randomtext2")
        C_Slots.property_unset("C_noise_depth2")
        C_Slots.property_unset("C_contrast2")
        C_Slots.property_unset("C_intensity2")
        C_Slots.property_unset("C_density_factor2")
        C_Slots.property_unset("C_length_factor2")
        C_Slots.property_unset("C_scalex2")
        C_Slots.property_unset("C_scaley2")
        C_Slots.property_unset("C_scalez2")
        C_Slots.property_unset("C_offsetx2")
        C_Slots.property_unset("C_offsety2")
        C_Slots.property_unset("C_offsetz2")
        C_Slots.property_unset("C_size_is_random2")
        C_Slots.property_unset("C_size_A2")
        C_Slots.property_unset("C_size_B2")
        C_Slots.property_unset("C_offset_is_random2")
        C_Slots.property_unset("C_offset_A2")
        C_Slots.property_unset("C_offset_B2")
        C_Slots.property_unset("C_use_band2")
        C_Slots.property_unset("C_band_turbulance2")

        C_Slots.property_unset("C_texture_or_img2")
        C_Slots.property_unset("C_texture_name2")
        C_Slots.property_unset("C_texture_uv2")
        return {'FINISHED'}  

class Scatter_MT_C_Slots_PresetMenu(bpy.types.Menu):
    bl_label = "Please choose a Preset"
    bl_idname = "Scatter_MT_C_Slots_PresetMenu"
    preset_subdir = "scatter_presets_custom"
    preset_operator = "script.execute_preset"
    
    draw = bpy.types.Menu.draw_preset


class SCATTER_OT_C_Slots_del_confirm(bpy.types.Operator):
    bl_idname = "scatter.c_slot_del_confirm"
    bl_label = "Do you really want to delete the active preset ?"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        #bpy.ops.scatter.custom_slot_preset_add_operator(remove_active=True)
        directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")

        os.remove(directory + bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label.lower().replace(" ", "_")+".jpg")
        os.remove(directory + bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label.lower().replace(" ", "_")+".py")

        i=0
        for ob in preview_collections["main"]:
            if i==0: bpy.data.window_managers["WinMan"].my_previews = ob ; i+=1

        bpy.ops.scatter.refresh_preview_img()
        bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(items=enum_previews_from_directory_items, update=update_and_exec_preset_from_enum) #somehow update lost track on delete and save
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class SCATTER_OT_C_Slots_Quick_addpreset(bpy.types.Operator):
    bl_idname      = "scatter.c_slots_quick_add_preset"
    bl_label       = "Reset the settings"
    bl_description = ""

    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        all_files = os.listdir(directory)
        py_files = [f for f in all_files if f[-3:] == ".py"]

        for ob in py_files:
            if ob[:-3].replace("_", " ") == C_Slots.C_name.lower().replace("_", " "):
                bpy.ops.wm.call_menu(name=SCATTER_PIE_confirm_overwrite.bl_idname) #confirm method like above didn't work #was forced to create menu + overator
                return {'FINISHED'}

        img_dir = directory + C_Slots.C_name.lower().replace(" ", "_")+".jpg"
        def_dir = directory + "__default_img__"
        if os.path.exists(def_dir):
            from shutil import copy2
            copy2(def_dir, img_dir) #copy default
        else:
            if os.path.isfile(img_dir) == False:
                from PIL import Image, ImageFont, ImageDraw
                # try: 
                #     W, H = (115,115)
                #     im = Image.new("RGB",(W,H),"black")
                #     draw = ImageDraw.Draw(im)
                #     w, h = draw.textsize(C_Slots.C_name)
                #     draw.text(((W-w)/2,(H-h)/2), C_Slots.C_name, fill="white")
                #     im.save(img_dir)
                # except:
                img = Image.new('RGB', (250, 250), color = 'black')
                img.save(img_dir)

        bpy.ops.scatter.custom_slot_preset_add_operator(name=C_Slots.C_name, remove_name=False, remove_active=False)
        bpy.ops.scatter.refresh_preview_img()
        bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(items=enum_previews_from_directory_items, update=update_and_exec_preset_from_enum) #somehow update lost track on delete and save
        bpy.data.window_managers["WinMan"].my_previews = C_Slots.C_name.lower().replace(" ","_") + ".jpg"
        ShowMessageBox('"'+C_Slots.C_name+ '" Preset is now in directory', "Saved" ,"COLORSET_03_VEC")
        return {'FINISHED'}

class SCATTER_OT_C_Slots_overwrite(bpy.types.Operator):
    bl_idname = "scatter.c_slot_overwrite_confirm"
    bl_label = "Do you really want to overwrite the active preset ?"
    bl_description = ""

    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        bpy.ops.scatter.custom_slot_preset_add_operator(name=C_Slots.C_name, remove_name=False, remove_active=False)
        ShowMessageBox('"'+C_Slots.C_name+ '" Preset is now in directory', "Saved" ,"COLORSET_03_VEC")
        return {'FINISHED'}

class SCATTER_PIE_confirm_overwrite(Menu): #problem first save and save as ? what ???????????????????????
    bl_label = ""
    bl_idname = "scatter_MT_confirm_dialog" #other id if two pies 

    def draw(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        layout = self.layout
        layout.label(text="OK?", icon="ERROR")
        layout.separator()
        layout.operator(SCATTER_OT_C_Slots_overwrite.bl_idname,text='Do you Really want to Overwrite "'+C_Slots.C_name+'" ?')


def scatter_presets_custom_folder_setup():
    #Make sure there is a directory for presets
    scatter_preset_subdir = "scatter_presets_custom"
    scatter_preset_directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", scatter_preset_subdir)
    scatter_preset_paths = bpy.utils.preset_paths(scatter_preset_subdir)
    if(scatter_preset_directory not in scatter_preset_paths):
        if(not os.path.exists(scatter_preset_directory)):
            os.makedirs(scatter_preset_directory)

class SCATTER_OT_Open_Directory(bpy.types.Operator):
    bl_idname      = "scatter.open_directory"
    bl_label       = "Open Directory"
    bl_description = ""

    def execute(self, context):
        scatter_preset_subdir = "scatter_presets_custom"
        scatter_preset_directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", scatter_preset_subdir)
        os.startfile(scatter_preset_directory)
        return {'FINISHED'} 

######################################################################################
#                               IMAGE PREVIEWS
######################################################################################

class SCATTER_OT_refresh_preview_img(bpy.types.Operator):
    bl_idname = "scatter.refresh_preview_img"
    bl_label = ""
    bl_description = "Refresh Previews"
    def execute(self, context):


        bpy.types.WindowManager.my_previews     = bpy.props.EnumProperty(items=enum_previews_from_directory_items)
        del bpy.types.WindowManager.my_previews
        bpy.types.WindowManager.my_textures     = bpy.props.EnumProperty(items=enum_previews_from_directory_text)
        del bpy.types.WindowManager.my_textures
        for pcoll in preview_collections.values(): bpy.utils.previews.remove(pcoll)
        
        preview_collections.clear()

        pcoll = bpy.utils.previews.new()
        pcoll.my_previews_dir = ""
        pcoll.my_previews = ()
        preview_collections["main"] = pcoll

        pcoll = bpy.utils.previews.new()
        pcoll.my_textures_dir = ""
        pcoll.my_textures = ()
        preview_collections["text"] = pcoll

        #debug
        bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(items=enum_previews_from_directory_items, update=update_and_exec_preset_from_enum) #somehow update lost track on delete and save
        bpy.types.WindowManager.my_textures = bpy.props.EnumProperty(items=enum_previews_from_directory_text)
        return {'FINISHED'}


# class SCATTER_OT_debug(bpy.types.Operator):
#     bl_idname      = "scatter.debug"
#     bl_label       = ""
#     bl_description = "preview debug"

#     def execute(self, context):
#         bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(items=enum_previews_from_directory_items, update=update_and_exec_preset_from_enum) #somehow update lost track on delete and save
#         return {'FINISHED'}


def enum_previews_from_directory_items(self, context):
    enum_items = []
    if context is None: return enum_items
    wm        = context.window_manager
    directory = wm.my_previews_dir

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.my_previews_dir:
        return pcoll.my_previews

    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".jpg"): image_paths.append(fn)#

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon     = pcoll.get(name)
            if not icon: thumb = pcoll.load(name, filepath, 'IMAGE')
            else:        thumb = pcoll[name]
            enum_items.append((name, name[:-4].replace("_"," ").title(), "", thumb.icon_id, i))

    pcoll.my_previews = enum_items
    pcoll.my_previews_dir = directory
    return pcoll.my_previews

######################################################################


def enum_previews_from_directory_text(self, context):
    enum_items = []
    if context is None: return enum_items
    wm        = context.window_manager
    directory = wm.my_textures_dir

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["text"]

    if directory == pcoll.my_textures_dir:
        return pcoll.my_textures

    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            #if fn.lower().endswith(".jpg"): 
            if "_invert" not in fn:
                image_paths.append(fn)#

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon     = pcoll.get(name)
            if not icon: thumb = pcoll.load(name, filepath, 'IMAGE')
            else:        thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.my_textures = enum_items
    pcoll.my_textures_dir = directory
    return pcoll.my_textures

######################################################################

class SCATTER_OT_skip_prev(bpy.types.Operator):
    bl_idname = "scatter.skip_prev"
    bl_label = ""
    bl_description = ""


    left0_right1 : bpy.props.IntProperty()
    def execute(self, context):
        left0_right1 = self.left0_right1

        addon_prefs = context.preferences.addons[__name__].preferences
        directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]

        list_choice=[]
        list_raw=[]
        active_enum = bpy.data.window_managers["WinMan"].my_previews[:-4].replace("_", " ").title()
        for f in onlyfiles:
            if f[-4:] == ".jpg":
                list_choice.append(f[:-4].replace("_", " ").title()) #Addon pref preset by defautl necessary !!!!
                list_raw.append(f)

        i = list_choice.index(active_enum)

        #PREV
        if left0_right1 ==0:
            if i == 0: return {'FINISHED'}#i=len(list_choice)#(already +1 as len don't start from 0) #loop
            bpy.data.window_managers["WinMan"].my_previews = list_raw[i-1]
        #NEXT
        elif left0_right1 ==1:
            if i == len(list_choice)-1:return {'FINISHED'} #i=-1 #loop
            bpy.data.window_managers["WinMan"].my_previews = list_raw[i+1]
        #FIRST
        elif left0_right1 ==2:
            i=0
            bpy.data.window_managers["WinMan"].my_previews = list_raw[i]
        #LAST
        elif left0_right1 ==3:
            i= len(list_choice)-1
            bpy.data.window_managers["WinMan"].my_previews = list_raw[i]

        return {'FINISHED'}



######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne
#
#  .oooooo.                                               .
# d8P'  `Y8b                                            .o8
#888      888 oo.ooooo.   .ooooo.  oooo d8b  .oooo.   .o888oo  .ooooo.  oooo d8b
#888      888  888' `88b d88' `88b `888""8P `P  )88b    888   d88' `88b `888""8P
#888      888  888   888 888ooo888  888      .oP"888    888   888   888  888
#`88b    d88'  888   888 888    .o  888     d8(  888    888 . 888   888  888
# `Y8bood8P'   888bod8P' `Y8bod8P' d888b    `Y888""8o   "888" `Y8bod8P' d888b
#              888
#             o888o
######################################################################################

######################################################################################
# # # # # # # # # # # #         MAIN OPERATOR                  # # # # # # # # # # # #
######################################################################################

class SCATTER_OT_C_Slots(bpy.types.Operator):
    bl_idname = "scatter.custom_slot_operator"
    bl_label = "Custom Scattering Operator"
    bl_description = ""

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        scene = bpy.context.scene
        A = C_Slots.Terrain_pointer
        Selection = bpy.context.selected_objects
        active_coll_name = bpy.context.view_layer.active_layer_collection.name

        ### ### error message
        if len(bpy.context.selected_objects) == 0:
            ShowMessageBox("Please have some particles in your selection", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        if len(bpy.context.selected_objects) == 1:
            if bpy.context.selected_objects[0] == A:
                ShowMessageBox("Please have some particles in your selection", "Be Careful" ,"ERROR")
                return {'FINISHED'}

        #delselect A because user is dummy
        if A in bpy.context.selected_objects: A.select_set(state=False)

        ### ### error message
        sc_ob = [c.name for c in bpy.context.scene.objects] 
        if A.name not in sc_ob:
            ShowMessageBox(A.name+" target has been deleted", "Be Careful" ,"ERROR")
            return {'FINISHED'}

         ### ### error message
        if (C_Slots.C_texture_type == "Texture" and C_Slots.C_texture_or_img1 == "Texture" and C_Slots.C_texture_name1 not in bpy.data.textures):
            ShowMessageBox(C_Slots.C_texture_name1+" texture is not in this .blend", "Be Careful" ,"ERROR")
            return {'FINISHED'}
        elif (C_Slots.C_texture_type == "Texture" and C_Slots.C_texture_or_img1 == "Image"):
            directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
            if C_Slots.C_texture_name1 not in os.listdir(directory+r'\__textures__'):
                ShowMessageBox(C_Slots.C_texture_name1+" image is not in __textures__", "Be Careful" ,"ERROR")
                return {'FINISHED'} 
        elif (C_Slots.C_texture_type == "Texture" and C_Slots.C_texture_or_img1 == "Terrain"):
            if A.name not in bpy.data.images:
                ShowMessageBox('"'+A.name+'" bake not in image data', "Be Careful" ,"ERROR")
                return {'FINISHED'}
        ### ### same 
        if (C_Slots.C_texture_type2 == "Texture" and C_Slots.C_texture_or_img2 == "Texture" and C_Slots.C_texture_name2 not in bpy.data.textures):
            ShowMessageBox(C_Slots.C_texture_name2+" texture is not in this .blend", "Be Careful" ,"ERROR")
            return {'FINISHED'}
        elif (C_Slots.C_texture_type2 == "Texture" and C_Slots.C_texture_or_img2 == "Image"):
            directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
            if C_Slots.C_texture_name2 not in os.listdir(directory+r'\__textures__'):
                ShowMessageBox(C_Slots.C_texture_name2+" image is not in __textures__", "Be Careful" ,"ERROR")
                return {'FINISHED'} 
        elif (C_Slots.C_texture_type2 == "Texture" and C_Slots.C_texture_or_img2 == "Terrain"):
            if A.name not in bpy.data.images:
                ShowMessageBox('"'+A.name+'" bake not in image data', "Be Careful" ,"ERROR")
                return {'FINISHED'}


        ### ### error message
        if addon_prefs.scatter_is_curve== True:
            if len(A.data.polygons) < 150:
                ShowMessageBox("Your terrain don't have enough geometry for the weight proximity modifier", "Be Careful" ,"ERROR")
                return {'FINISHED'}
        ### ### error message
        for ob in Selection:
            if ob != A:
                for o in bpy.data.collections:
                    if o.name == "Scatter: ["+ob.name+"]"+" Particles" : 
                        ShowMessageBox("you are not allowed to use an active terrain as a particle", "Be Careful" ,"ERROR")
                        return {'FINISHED'}
        ### ### remove unwanted object
        for ob in Selection:
            if ob.type != 'MESH': ob.select_set(state=False)
        ### ### error message prox
        prox =0 ; not_prox=0
        for ob in bpy.context.selected_objects:
            if '[proxy]' in ob.name:
                prox +=1
                addon_prefs.scatter_is_not_batch = True
            if '[proxy]' not in ob.name: not_prox +=1
        if prox !=0:
            if not_prox != prox:
                ShowMessageBox("Each particles need it's own proxies", "Be Careful" ,"ERROR")
                return {'FINISHED'}

        ### ### set all system
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True) #apply scale on all selection
        #A = bpy.context.object????????????????????????????????
        if addon_prefs.scatter_is_not_batch == False: #BATCH EACH OBJ IN SELECTION = OWN PARTICLE SYSTEM
            for ob in bpy.context.selected_objects: #not accessible yet
                if ob != A:
                    c_slots_op(ob,A)
                    attribute_default_vgroup_if_not(A,ob)
        else: #ALL SELECT = COLL
            counter=0
            for ob in bpy.context.selected_objects:
                if ob != A:
                    if counter ==0:
                        #below = better perf ? maybe
                        partviewporttrue = []
                        for p in A.particle_systems:
                            if "SCATTER" in p.name:
                                if A.modifiers[p.name].show_viewport == True:
                                    partviewporttrue.append(p.name)
                                    A.modifiers[p.name].show_viewport = False
    
                        c_slots_op(ob,A)
                        attribute_default_vgroup_if_not(A,ob)
                        counter+=1
                        #below = better perf ? maybe
                        for name in partviewporttrue: A.modifiers[name].show_viewport = True

                    else:
                        if addon_prefs.scatter_is_bounds == True: #bounds not checked
                            if "proxy" not in ob.name: ob.display_type = 'BOUNDS'
                        if len(ob.data.polygons) > addon_prefs.scatter_bound_if_more: ob.display_type = 'BOUNDS'

                        ob_old_coll = ob.users_collection 
                        bpy.context.scene.collection.children[-1].children[-1].objects.link(ob)
                        for o in ob_old_coll: #remove from coll after link if not scatter coll
                            if "SCATTER:" not in o.name: o.objects.unlink(ob)

        ### ### unselect all other particles sys from A and select last one. 
        for p in A.particle_systems:
            if p != A.particle_systems[-1]: p.settings["is_selected"] = 0

        ### ### set up proxies
        if prox !=0:
            bpy.ops.scatter.set_up_proxy()

        ### ### restore active collection change
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection,active_coll_name)
        bpy.context.view_layer.active_layer_collection = layerColl

        ### #### force particles to update
        Sel = bpy.context.selected_objects
        for ob in Sel:
            if ob.name != A.name: ob.select_set(state=False)
        bpy.ops.object.editmode_toggle() ; bpy.ops.object.editmode_toggle()
        bpy.ops.particle.dupliob_refresh()
        for ob in Sel: ob.select_set(state=True)

        ## ### curve auto
        exec_boolean = False
        if addon_prefs.scatter_is_curve== True:
            for ob in Selection:
                if ob.type == 'CURVE':
                    ob.select_set(state=True)
                    exec_boolean = True
            if exec_boolean == True: bpy.ops.scatter.bool_path()

        ## ### curve auto
        exec_cam = False
        if addon_prefs.scatter_is_camera== True:
            for ob in Selection:
                if ob.type == 'CAMERA':
                    bpy.context.scene.camera = ob
                    exec_cam = True
            if exec_cam == True: bpy.ops.scatter.camera_crop_and_density()

        return {'FINISHED'}

######################################################################################
# # # # # # # # # # # #          MAIN OP DEF                   # # # # # # # # # # # #
######################################################################################

def c_slots_op(ob,a):
    bm = bmesh.new()
    bm.from_mesh(a.data) 
    squarearea = sum(f.calc_area() for f in bm.faces)
    bm.free()

    C_Slots     = bpy.context.scene.C_Slots_settings
    addon_prefs = context.preferences.addons[__name__].preferences
    slotname    = C_Slots.C_name
    #bpy.context.object

    ### ### if bounds
    if addon_prefs.scatter_is_bounds == True:
        if "proxy" not in ob.name:
            ob.display_type = 'BOUNDS'
    if ob.display_type != 'BOUNDS':
        if len(ob.data.polygons) > addon_prefs.scatter_bound_if_more:
            ob.display_type = 'BOUNDS'
            ShowMessageBox("Object automatically displayed as bounding box.  (->On Creation Display)", "Polycount too high !",'ERROR')

    ### ### ### collection creation
    ob_old_coll = ob.users_collection 
    terrain_coll_name = "SCATTER: ["+a.name+"]"+" Particles"
    if terrain_coll_name not in bpy.data.collections: #CREATE MAIN TERRAIN COLLECTION if not already there
        terrain_coll = bpy.data.collections.new(name=terrain_coll_name)
        bpy.context.scene.collection.children.link(terrain_coll)
    else:
        terrain_coll = bpy.data.collections[terrain_coll_name]
    particle_coll = bpy.data.collections.new(name="SCATTER: ["+slotname+"] "+addon_prefs.scatter_particles_sys_name+".000") #name but will be corrected .00X ! 
    bpy.data.collections[terrain_coll_name].children.link(particle_coll) #put new coll in terrain coll created above
    particle_coll.objects.link(ob) #link ob to particle  coll
    for o in ob_old_coll: #unlink from all  precedent obj collections
        if "SCATTER:" not in o.name: #unlink only from non particle_coll
            o.objects.unlink(ob)
    name = particle_coll.name #true name of the corrected collection 

    ### ### ### purge unused particles data
    for psdata in bpy.data.particles:
        if psdata.name[:7] == 'SCATTER':
            if psdata.users == 0: bpy.data.particles.remove(psdata, do_unlink=True)

    ### ### ### purge unused texture data
    for txdata in bpy.data.textures:
       if txdata.name[:7] == 'SCATTER':
            if txdata.users == 0: bpy.data.textures.remove(txdata, do_unlink=True)

    ### ### ### particle parameters
    m = a.modifiers.new(name, type='PARTICLE_SYSTEM')
    ps = m.particle_system
    ps.name = name
    a.modifiers[name].show_viewport = False #optimisation purpose
    ps.settings.name = name
    ps.settings.type = 'HAIR'
    ps.settings.render_type = 'COLLECTION'
    ps.settings.instance_collection = bpy.data.collections[name]
    ps.settings.particle_size = C_Slots.C_particle_size
    ps.settings.hair_length = 1
    ps.settings.size_random = C_Slots.C_size_random
    ps.settings.use_modifier_stack = True

    if (C_Slots.C_per_vert == True or C_Slots.C_per_face == True): ##
        ps.settings.use_emit_random = False
        ps.settings.userjit = 1
        C_Slots.C_countispersquare = 'None'
        C_Slots.C_use_children = False
        if C_Slots.C_per_vert == True:
            ps.settings.emit_from = 'VERT'
            C_Slots.C_count = len(a.data.vertices)
        else:
            ps.settings.emit_from = 'FACE'
            C_Slots.C_count = len(a.data.polygons)

    if C_Slots.C_countispersquare   == '/m²': ps.settings.count  = C_Slots.C_countpersquare * squarearea
    elif C_Slots.C_countispersquare == '/km²': ps.settings.count = C_Slots.C_countpersquare * (squarearea/1000)
    elif C_Slots.C_countispersquare == 'None': ps.settings.count = C_Slots.C_count

    if C_Slots.C_seed_is_random == True: ps.seed = random.randint(0,10000)
    else: ps.seed = C_Slots.C_seed

    ps.settings.display_percentage = addon_prefs.scatter_percentage
    ps.settings.use_advanced_hair = True
    ps.settings.use_rotations = True

    if C_Slots.C_orientation   == "GlobalZ" : ps.settings.rotation_mode = 'GLOB_Z'
    elif C_Slots.C_orientation == "NormalZ" : ps.settings.rotation_mode = 'NOR'
    elif C_Slots.C_orientation == "LocalZ"  : ps.settings.rotation_mode = 'OB_Z'

    ps.settings.rotation_factor_random = C_Slots.C_phase_rotation
    ps.settings.phase_factor = 1
    ps.settings.phase_factor_random = C_Slots.C_phase_factor_random
    if C_Slots.C_per_face != True: ps.settings.distribution = 'RAND'

    ### ### ### children
    if C_Slots.C_use_children == True:
        ps.settings.child_type = 'INTERPOLATED'
        ps.settings.child_nbr            = C_Slots.C_children_ammount
        ps.settings.rendered_child_count = C_Slots.C_children_ammount
        ps.settings.roughness_1          = C_Slots.C_children_roughness
        ps.settings.roughness_1_size     = C_Slots.C_children_roughness_s
        ps.settings.clump_factor         = C_Slots.C_children_clump

    ### ### ### selection boolean values is_bounds
    bpy.data.particles[name]["is_selected"] = 1
    bpy.data.particles[name]["is_proxy"] = 'Not Yet'

    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX

    if (C_Slots.C_texture_type == "Automatic" or C_Slots.C_texture_type == "Texture"):

        bpy.ops.texture.new()

        if C_Slots.C_noise_randomtext == True:
            bpy.data.textures[-1].contrast  = round(random.uniform(1.5,5),2)
            bpy.data.textures[-1].intensity = round(random.uniform(0.3,0.9),2)
        else:
            bpy.data.textures[-1].contrast  = C_Slots.C_contrast 
            bpy.data.textures[-1].intensity = C_Slots.C_intensity 

        ps.settings.texture_slots.add().texture = bpy.data.textures[-1]
        ps.settings.texture_slots[0].blend_type      = 'MULTIPLY'
        ps.settings.texture_slots[0].use_map_time    = False
        ps.settings.texture_slots[0].use_map_density = True
        ps.settings.texture_slots[0].use_map_length  = True 
        ps.settings.texture_slots[0].density_factor  = C_Slots.C_density_factor
        ps.settings.texture_slots[0].length_factor   = C_Slots.C_length_factor
        ps.settings.texture_slots[0].texture_coords  = 'GLOBAL'
        texture_mapping(0,ps,C_Slots.C_scalex,C_Slots.C_scaley,C_Slots.C_scalez,C_Slots.C_size_A,C_Slots.C_size_B,C_Slots.C_offsetx,C_Slots.C_offsety,C_Slots.C_offsetz,C_Slots.C_offset_A,C_Slots.C_offset_B,C_Slots.C_size_is_random,C_Slots.C_offset_is_random)

        if C_Slots.C_texture_type == "Automatic":####################### ###

            texturename                = name+"_TEX1"
            bpy.data.textures[-1].name = texturename
            if C_Slots.C_use_band == True:
                bpy.data.textures[texturename].type       = 'WOOD'
                bpy.data.textures[texturename].wood_type  = 'BANDNOISE'
                bpy.data.textures[texturename].turbulence = C_Slots.C_band_turbulance
            else:
                bpy.data.textures[texturename].type = 'CLOUDS'
            if C_Slots.C_noise_scaleisrandom == True:
                bpy.data.textures[texturename].noise_scale = round(random.uniform(C_Slots.C_noise_scaleA,C_Slots.C_noise_scaleB), 2)
            else:
                bpy.data.textures[texturename].noise_scale = C_Slots.C_noise_scale
            if C_Slots.C_use_band == False:
                bpy.data.textures[texturename].noise_depth = C_Slots.C_noise_depth 

        if C_Slots.C_texture_type == "Texture":######################## ###

            if C_Slots.C_texture_or_img1 =='Texture':################## # #
                ps.settings.texture_slots.add().texture = bpy.data.textures[C_Slots.C_texture_name1]

            elif C_Slots.C_texture_or_img1 =='Image':################## # #
                texturename                = name+"_IMG1"
                bpy.data.textures[-1].name = texturename
                bpy.data.textures[texturename].type = 'IMAGE'
                directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
                filepath  = directory + '\\__textures__\\'  + C_Slots.C_texture_name1
                if  C_Slots.C_texture_name1 not in bpy.data.images:
                    bpy.ops.image.open(filepath=filepath)
                bpy.data.textures[texturename].image = bpy.data.images[C_Slots.C_texture_name1]
 
            elif C_Slots.C_texture_or_img1 =='Terrain':################## # #
                texturename                = name+"_UV1"
                bpy.data.textures[-1].name = texturename
                bpy.data.textures[texturename].type = 'IMAGE'
                bpy.data.textures[texturename].image = bpy.data.images[a.name]

            if (C_Slots.C_texture_uv1 == True or C_Slots.C_texture_or_img1 =='Terrain'):
                ps.settings.texture_slots[0].texture_coords   = 'UV'
            else: ps.settings.texture_slots[0].texture_coords = 'GLOBAL'



    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX

    if (C_Slots.C_texture_type2 == "Automatic" or C_Slots.C_texture_type2 == "Texture"):

        bpy.ops.texture.new()

        if C_Slots.C_noise_randomtext2 == True:
            bpy.data.textures[-1].contrast  = round(random.uniform(1.5,5),2)
            bpy.data.textures[-1].intensity = round(random.uniform(0.3,0.9),2)
        else:
            bpy.data.textures[-1].contrast  = C_Slots.C_contrast2
            bpy.data.textures[-1].intensity = C_Slots.C_intensity2 

        ps.settings.texture_slots.add().texture      = bpy.data.textures[-1]
        ps.settings.texture_slots[1].blend_type      = 'MULTIPLY'
        ps.settings.texture_slots[1].use_map_time    = False
        ps.settings.texture_slots[1].use_map_density = True
        ps.settings.texture_slots[1].use_map_length  = True 
        ps.settings.texture_slots[1].density_factor  = C_Slots.C_density_factor2
        ps.settings.texture_slots[1].length_factor   = C_Slots.C_length_factor2
        ps.settings.texture_slots[1].texture_coords  = 'GLOBAL'
        texture_mapping(1,ps,C_Slots.C_scalex2,C_Slots.C_scaley2,C_Slots.C_scalez2,C_Slots.C_size_A2,C_Slots.C_size_B2,C_Slots.C_offsetx2,C_Slots.C_offsety2,C_Slots.C_offsetz2,C_Slots.C_offset_A2,C_Slots.C_offset_B2,C_Slots.C_size_is_random2,C_Slots.C_offset_is_random2)

        if C_Slots.C_texture_type2 == "Automatic":####################### ###

            texturename                = name+" _TEX2"
            bpy.data.textures[-1].name = texturename
            bpy.data.particles[name].active_texture_index = 1

            if C_Slots.C_use_band2 == True:
                bpy.data.textures[texturename].type       = 'WOOD'
                bpy.data.textures[texturename].wood_type  = 'BANDNOISE'
                bpy.data.textures[texturename].turbulence = C_Slots.C_band_turbulance2
            else:
                bpy.data.textures[texturename].type = 'CLOUDS'

            if C_Slots.C_noise_scaleisrandom2 == True:
                bpy.data.textures[texturename].noise_scale = round(random.uniform(C_Slots.C_noise_scaleA2,C_Slots.C_noise_scaleB2), 2)
            else:
                bpy.data.textures[texturename].noise_scale = C_Slots.C_noise_scale2
            if C_Slots.C_use_band2 == False:
                bpy.data.textures[texturename].noise_depth = C_Slots.C_noise_depth2 


        if C_Slots.C_texture_type2 == "Texture":######################## ###

            if C_Slots.C_texture_or_img2 =='Texture':################## # #
                ps.settings.texture_slots.add().texture = bpy.data.textures[C_Slots.C_texture_name2]

            elif C_Slots.C_texture_or_img2 =='Image':################## # #
                texturename                = name+"_IMG2"
                bpy.data.textures[-1].name = texturename
                bpy.data.textures[texturename].type     = 'IMAGE'
                directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
                filepath  = directory + '\\__textures__\\'  + C_Slots.C_texture_name2
                if  C_Slots.C_texture_name2 not in bpy.data.images:
                    bpy.ops.image.open(filepath=filepath)
                bpy.data.textures[texturename].image = bpy.data.images[C_Slots.C_texture_name2]
 
            elif C_Slots.C_texture_or_img2 =='Terrain':################## # #
                texturename                = name+"_UV2"
                bpy.data.textures[-1].name = texturename
                bpy.data.textures[texturename].type  = 'IMAGE'
                bpy.data.textures[texturename].image = bpy.data.images[a.name]

            if (C_Slots.C_texture_uv2 == True or C_Slots.C_texture_or_img2 =='Terrain'):
                ps.settings.texture_slots[0].texture_coords   = 'UV'
            else: ps.settings.texture_slots[0].texture_coords = 'GLOBAL'


    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX
    #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX #TEX

    ### automatic display % reduction
    msg = 0
    if ps.settings.count > addon_prefs.scatter_perc_if_more:
        num = ps.settings.count
        max = addon_prefs.scatter_perc_if_more
        per = int((max/num)*100)
        if per == 0: per = 1
        ps.settings.display_percentage = per
        msg += 1
        
    ### hide on creation 
    a.modifiers[name].show_expanded = False
    if addon_prefs.scatter_is_not_disp==True:  a.modifiers[name].show_viewport = False
    else: a.modifiers[name].show_viewport = True
    ### hide if above C
    if ps.settings.count >= addon_prefs.scatter_nodisp_if_more:
        a.modifiers[name].show_viewport = False
        msg += 1

    if msg ==1: ShowMessageBox("percentage display adjusted accordingly.  (->On Creation Display)", "Particle count too high !",'ERROR')
    elif msg ==2: ShowMessageBox("the particle system was autmatically hidden.  (->On Creation Display)", "Particle count way too high !",'ERROR')


   
def modifier_always_on_top(b): #useless ? just for displace modifiers ? + not optimized ans stupid ? 40 x? 
    for a in range (40):
        bpy.ops.object.modifier_move_up(modifier=b)

def attribute_default_vgroup_if_not(a,ob):
    addon_prefs = context.preferences.addons[__name__].preferences
    C_Slots     = bpy.context.scene.C_Slots_settings

    if bpy.context.scene.collection.children["SCATTER: ["+a.name+"]"+" Particles"].children[-1].name not in a.vertex_groups: #if the vgroup not in terrain then prlly never set up the system

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = C_Slots.Terrain_pointer
        C_Slots.Terrain_pointer.select_set(state=True)

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.vertex_group_add()
        bpy.context.object.vertex_groups[len(a.vertex_groups)-1].name = bpy.context.scene.collection.children["SCATTER: ["+a.name+"]"+" Particles"].children[-1].name
        bpy.context.scene.tool_settings.vertex_group_weight = 1
        bpy.ops.object.vertex_group_assign()
        bpy.ops.object.editmode_toggle()

        C_Slots.Terrain_pointer.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

    a.particle_systems[bpy.context.scene.collection.children["SCATTER: ["+a.name+"]"+" Particles"].children[-1].name].vertex_group_density = bpy.context.scene.collection.children["SCATTER: ["+a.name+"]"+" Particles"].children[-1].name

def texture_mapping(x,ps,csx,csy,csz,csa,csb,cox,coy,coz,coa,cob,csr,cor):
    if csr == False: ps.settings.texture_slots[x].scale = (csx,csy,csz)
    else:
        randomn =round(random.uniform(csa,csb), 2)
        ps.settings.texture_slots[x].scale = (randomn,randomn,randomn)
    if cor == False: ps.settings.texture_slots[x].offset = (cox,coy,coz)
    else:
        randomno =round(random.uniform(coa,cob), 2)
        ps.settings.texture_slots[x].offset = (randomno,randomno,randomno)

def recurLayerCollection(layerColl, collName): #used for make a collection active
    found = None
    if (layerColl.name == collName): return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found: return found

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

######################################################################################
# # # # # # # # # # # #        MAIN OP OPEN PREF               # # # # # # # # # # # # 
######################################################################################

class SCATTER_OT_parameter(bpy.types.Operator):
    bl_idname = "scatter.parameter" #create bl id name 
    bl_label = ""
    bl_description = "Invoke addon pref Scatter parameters"

    def execute(self, context): 
        OLDareaUI = bpy.context.area.ui_type
        bpy.context.area.ui_type = 'PREFERENCES'
        bpy.context.preferences.active_section= 'ADDONS'
        bpy.context.window_manager.addon_support = {'COMMUNITY'}
        bpy.ops.preferences.addon_expand(module="Scatter_V1_05")
        bpy.context.window_manager.addon_search='Scatter [BD3D]'
        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        if platform.system() == 'Windows': #code below won't work on other OS
            Active_W = ctypes.windll.user32.GetActiveWindow()
            ctypes.windll.user32.SetWindowPos(Active_W, -1, 0, 0, 800, 1100,0x0002)#annule le cursor move, dont care for this one
        bpy.context.area.ui_type = OLDareaUI
        return {'FINISHED'}


class SCATTER_OT_active_to_target(bpy.types.Operator):
    bl_idname = "scatter.active_to_target"
    bl_label = ""
    bl_description = "asign Active object as Target"
    
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings 
        A = bpy.context.object
        if A:
            if A.type == 'MESH': C_Slots.Terrain_pointer = A
        return {'FINISHED'}

######################################################################################
# # # # # # # # # # # #            TERRAIN ACTIVE               # # # # # # # # # # # 
######################################################################################

class SCATTER_OT_terrain_is_active(bpy.types.Operator):
    bl_idname = "scatter.terrain_is_active"
    bl_label = ""
    bl_description = "Constantly use the active object as Terrain"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings

        addon_prefs.active_is_terrain = not addon_prefs.active_is_terrain

        if addon_prefs.active_is_terrain == True:
            print("start timer")
            bpy.app.handlers.depsgraph_update_post.append(h)
        return {'FINISHED'}

ao = None

def h(s):
    # just for testing, normally i won't use global
    #global ao

    C_Slots    = bpy.context.scene.C_Slots_settings       
    addon_prefs = context.preferences.addons[__name__].preferences

    if addon_prefs.active_is_terrain == False:
        print("stop timer")
        bpy.app.handlers.depsgraph_update_post.clear()

    ao = C_Slots.Terrain_pointer

    o = bpy.context.active_object
    if(ao != o):
        #if o.type =='MESH':
        ao = o
        print("yes")
        C_Slots.Terrain_pointer = ao

######################################################################################
# # # # # # # # # # # #      MAIN OP HOW MUCH IS THAT           # # # # # # # # # # # 
######################################################################################

class SCATTER_OT_how_much(bpy.types.Operator):
    bl_idname = "scatter.how_much" #create bl id name 
    bl_label = ""
    bl_description = "calculate the total ammount of particles"

    def execute(self, context): 
        C_Slots  = bpy.context.scene.C_Slots_settings
        Terrain  = C_Slots.Terrain_pointer

        Active    = bpy.context.object
        Selection = bpy.context.selected_objects
        for o in Selection: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)#need to apply otherwise false calculation.

        bm = bmesh.new()
        bm.from_mesh(Terrain.data)
        squarearea = sum(f.calc_area() for f in bm.faces)
        bm.free()
        locale.setlocale(locale.LC_ALL, 'en_US') 
        if C_Slots.C_countispersquare == '/m²' : total = C_Slots.C_countpersquare * squarearea          ; area = str(locale.format("%d", int(squarearea), grouping=True)) + " m²"
        if C_Slots.C_countispersquare == '/km²': total = C_Slots.C_countpersquare * (squarearea/1000)   ; area = str(locale.format("%d", int(squarearea/1000), grouping=True)) + " km²"
        ShowMessageBox("["+str(locale.format("%d", int(total), grouping=True))+"] particles will be created on an ["+ area+"] terrain", "How Much is that?" ,"OUTLINER_OB_LIGHT")

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = Active
        for o in Selection: o.select_set(state=True)

        return {'FINISHED'}


class SCATTER_OT_how_much2(bpy.types.Operator):
    bl_idname = "scatter.how_much2" #create bl id name
    bl_label = ""
    bl_description = "calculate the total ammount of particles"

    def execute(self, context): 

        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots  = bpy.context.scene.C_Slots_settings
        Terrain  = C_Slots.Terrain_pointer

        Active    = bpy.context.object
        Selection = bpy.context.selected_objects
        for o in Selection: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)#need to apply otherwise false calculation. 

        bm = bmesh.new()
        bm.from_mesh(Terrain.data) 
        squarearea = sum(f.calc_area() for f in bm.faces)
        bm.free()
        locale.setlocale(locale.LC_ALL, 'en_US')
        if addon_prefs.persquaremorkm == '/m²' : total = addon_prefs.persquarem * squarearea          ; area = str(locale.format("%d", int(squarearea), grouping=True)) + " m²"
        if addon_prefs.persquaremorkm == '/km²': total = addon_prefs.persquarem * (squarearea/1000)   ; area = str(locale.format("%d", int(squarearea/1000), grouping=True)) + " km²"
        ShowMessageBox("["+str(locale.format("%d", int(total), grouping=True))+"] particles will be created on an ["+ area+"] terrain", "How Much is that?" ,"OUTLINER_OB_LIGHT")

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = Active
        for o in Selection: o.select_set(state=True)

        return {'FINISHED'}


class SCATTER_OT_particles_orientation(bpy.types.Operator):
    bl_idname = "scatter.particles_orientation" #create bl id name
    bl_label = ""
    bl_description = "calculate the total ammount of particles"

    option : bpy.props.StringProperty()
    def execute(self, context):
        option=self.option

        C_Slots  = bpy.context.scene.C_Slots_settings
        Terrain  = C_Slots.Terrain_pointer

        for ob in Terrain.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    Terrain.particle_systems[ob.name].settings.rotation_mode = option
        #bpy.data.particles[particles].rotation_mode = option #GLOB_Z NOR VEL OB_Z
        return {'FINISHED'}


##############################################################################################
#
#  .oooooo.   ooooooooo.         .oooooo..o oooo   o8o        .o8
# d8P'  `Y8b  `888   `Y88.      d8P'    `Y8 `888   `"'       "888
#888      888  888   .d88'      Y88bo.       888  oooo   .oooo888   .ooooo.  oooo d8b  .oooo.o
#888      888  888ooo88P'        `"Y8888o.   888  `888  d88' `888  d88' `88b `888""8P d88(  "8
#888      888  888                   `"Y88b  888   888  888   888  888ooo888  888     `"Y88b.
#`88b    d88'  888              oo     .d8P  888   888  888   888  888    .o  888     o.  )88b
# `Y8bood8P'  o888o             8""88888P'  o888o o888o `Y8bod88P" `Y8bod8P' d888b    8""888P'
#
##############################################################################################

class SCATTER_OT_slider_create_tex(bpy.types.Operator):
    bl_idname = "scatter.create_tex"
    bl_label = ""
    
    name_1 : bpy.props.StringProperty() # defining the property
    def execute(self, context):
        name_1 = self.name_1

        C_Slots     = bpy.context.scene.C_Slots_settings
        Terrrain = C_Slots.Terrain_pointer

        if name_1 not in bpy.data.textures:
            bpy.ops.texture.new()
            bpy.data.textures[-1].name = name_1
        bpy.data.textures[name_1].type = 'CLOUDS'
        bpy.data.textures[name_1].noise_scale = 1.5
        bpy.data.textures[name_1].contrast = 3
        if Terrrain.particle_systems[name_1].settings.texture_slots[0] == None:
            Terrrain.particle_systems[name_1].settings.texture_slots.add().texture = bpy.data.textures[name_1]
        if Terrrain.particle_systems[name_1].settings.texture_slots[0].name == "":
            Terrrain.particle_systems[name_1].settings.texture_slots[0].texture    = bpy.data.textures[name_1]

        Terrrain.particle_systems[name_1].settings.texture_slots[0].blend_type      = 'MULTIPLY'
        Terrrain.particle_systems[name_1].settings.texture_slots[0].use_map_time    = False
        Terrrain.particle_systems[name_1].settings.texture_slots[0].use_map_density = True
        Terrrain.particle_systems[name_1].settings.texture_slots[0].density_factor  = 1
        Terrrain.particle_systems[name_1].settings.texture_slots[0].use_map_length  = True 
        Terrrain.particle_systems[name_1].settings.texture_slots[0].length_factor   = 1
        Terrrain.particle_systems[name_1].settings.texture_slots[0].texture_coords  = 'GLOBAL'
        return {'FINISHED'}
    
class SCATTER_OT_slider_boolean(bpy.types.Operator):
    bl_idname = "scatter.boolean_toggle_slots"
    bl_label = ""
    
    property_1 : bpy.props.StringProperty()
    def execute(self, context):
        if bpy.data.particles[self.property_1]["is_selected"] == 1:
            bpy.data.particles[self.property_1]["is_selected"] = 0
        else: bpy.data.particles[self.property_1]["is_selected"] = 1
        return {'FINISHED'}

class SCATTER_OT_slider_persquaremeters(bpy.types.Operator):
    bl_idname = "scatter.persquaremeters"
    bl_label = ""
    
    persquare_obj : bpy.props.StringProperty()
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bm = bmesh.new()
        bm.from_mesh(A.data) 
        squarearea = sum(f.calc_area() for f in bm.faces)
        bm.free()
        
        if addon_prefs.persquaremorkm == '/m²':
            A.particle_systems[self.persquare_obj].settings.count =  addon_prefs.persquarem * squarearea
        if addon_prefs.persquaremorkm == '/km²':
            A.particle_systems[self.persquare_obj].settings.count =  addon_prefs.persquarem * (squarearea/1000)
        return {'FINISHED'}
    
    
class SCATTER_OT_slider_remov_system(bpy.types.Operator):
    bl_idname = "scatter.remov"
    bl_label = ""
    
    remov_obj : bpy.props.StringProperty()
    def execute(self, context):
        remov_obj=self.remov_obj


        C_Slots = bpy.context.scene.C_Slots_settings
        A       = C_Slots.Terrain_pointer

        Active = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        A.select_set(state=True)

        i=0
        remove="no"
        for ob in range (len(A.particle_systems)):
            if A.particle_systems[i].name == remov_obj:
                A.particle_systems.active_index=i
                remove="yes"
            i+=1
        if remove =="yes": bpy.ops.object.particle_system_remove()

        terrain_coll_name = "SCATTER: ["+A.name+"]"+" Particles"
        for coll_child in bpy.data.collections[terrain_coll_name].children:
            if coll_child.name not in A.particle_systems:
                if coll_child.name != "CAM-CUT: Camera-Clip":
                    for obj in bpy.data.collections[coll_child.name].objects:
                        if obj.name not in bpy.context.scene.collection.objects:
                            bpy.context.scene.collection.objects.link(obj)
                        bpy.data.collections[coll_child.name].objects.unlink(obj)
                    bpy.data.collections.remove(bpy.data.collections[coll_child.name])
        n=0 
        for p in A.particle_systems:
            if "SCATTER" in p.name: n+=1
        if n==0: bpy.ops.scatter.delete_cam()

        if len(bpy.data.collections[terrain_coll_name].children) ==0:
            bpy.data.collections.remove(bpy.data.collections[terrain_coll_name])

        for m in A.modifiers:
            if remov_obj[9:] in m.name:
                bpy.ops.object.modifier_remove(modifier=m.name)

        for vg in A.vertex_groups:
            if remov_obj in vg.name:
                bpy.ops.object.vertex_group_set_active(group=vg.name)
                bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

        A.select_set(state=False)
        bpy.context.view_layer.objects.active = Active
        for o in S: o.select_set(state=True)

        return {'FINISHED'}

######################################################################################
# # # # # # # # # # # #            SLIDERS IMG                # # # # # # # # # # # # 
######################################################################################

class SCATTER_OT_slider_img_enum_choose(bpy.types.Operator):
    bl_idname = "scatter.img_enum_choose"
    bl_label = ""

    i             : bpy.props.IntProperty()
    particle_name : bpy.props.StringProperty() 
    def execute(self, context):
        particle_name = self.particle_name
        i             = self.i

        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings
        enum_choi   = bpy.data.window_managers["WinMan"].my_textures
        directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        filepath    = directory + '\\__textures__\\'  + enum_choi
        Terrain     = C_Slots.Terrain_pointer

        if enum_choi not in bpy.data.images:
            bpy.ops.image.open(filepath=filepath)
            #bpy.data.images[-1].name = enum_choi

        Terrain.modifiers[particle_name].particle_system.settings.texture_slots[i].texture.image = bpy.data.images[enum_choi]

        if addon_prefs.region_refresh == True: addon_prefs.region_refresh = False
        elif addon_prefs.region_refresh == False: addon_prefs.region_refresh = True
        return {'FINISHED'}


class SCATTER_OT_slider_img_create_invert(bpy.types.Operator):
    bl_idname = "scatter.img_create_invert"
    bl_label = ""
    bl_description = "create an invert version of every texture in directory if not already there (you will need to refresh)"

    i             : bpy.props.IntProperty()
    img           : bpy.props.StringProperty()
    particle_name : bpy.props.StringProperty()
    def execute(self, context):
        i             = self.i
        img           = self.img
        particle_name = self.particle_name

        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots     = bpy.context.scene.C_Slots_settings
        Terrain     = C_Slots.Terrain_pointer

        directory  = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        filepath1  = directory + '\\__textures__\\'
        filepath2  = directory + '\\__textures__\\__inverted__\\'

        from os import listdir
        from os.path import isfile, join
        filelist1 = [f for f in listdir(filepath1) if isfile(join(filepath1, f))]
        filelist2 = [f for f in listdir(filepath2) if isfile(join(filepath2, f))]
        filelist  = filelist1 + filelist2

        if img not in filelist:
            ShowMessageBox("Invert operation is only for textures in __textures__ folder", "Be Carreful",'ERROR')
            return {'FINISHED'}
        
        if "_invert_" not in img:
            if "_invert_" + img not in filelist:
                from PIL import Image
                import PIL.ImageOps    
                image = Image.open(filepath1 + img)
                inverted_image = PIL.ImageOps.invert(image)
                inverted_image.save(filepath2 +"_invert_"+img)

        if "_invert_" not in img:
            if "_invert_" + img not in bpy.data.images:
                bpy.ops.image.open(filepath=filepath2 +"_invert_" + img)

        if "_invert_" not in img:
            Terrain.modifiers[particle_name].particle_system.settings.texture_slots[i].texture.image = bpy.data.images["_invert_" + img]
        elif "_invert_" in img:
            Terrain.modifiers[particle_name].particle_system.settings.texture_slots[i].texture.image = bpy.data.images[ img.replace("_invert_","") ]

        if addon_prefs.region_refresh == True: addon_prefs.region_refresh = False
        elif addon_prefs.region_refresh == False: addon_prefs.region_refresh = True
        return {'FINISHED'}


class SCATTER_OT_img_skip_prev(bpy.types.Operator):
    bl_idname = "scatter.img_skip_prev"
    bl_label = ""
    bl_description = ""

    i             : bpy.props.IntProperty()
    left0_right1  : bpy.props.IntProperty()
    particle_name : bpy.props.StringProperty()
    def execute(self, context):
        left0_right1  = self.left0_right1
        particle_name = self.particle_name
        i             = self.i
        intt = i

        #bpy.ops.scatter.refresh_preview_img()

        directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        filepath  = directory + '\\__textures__\\'
        filelist = os.listdir(filepath)

        list_choice=[]
        active_enum = bpy.data.window_managers["WinMan"].my_textures
        
        for f in filelist:
            if "_invert" not in f:
                list_choice.append(f)

        i = list_choice.index(active_enum)

        #PREV
        if left0_right1 ==0:
            if i == 0: i=len(list_choice)#(already +1 as len don't start from 0) #loop
            bpy.data.window_managers["WinMan"].my_textures = list_choice[i-1]
        #NEXT
        elif left0_right1 ==1:
            if i == len(list_choice)-1: i=-1 #loop
            bpy.data.window_managers["WinMan"].my_textures = list_choice[i+1]

        bpy.ops.scatter.img_enum_choose(particle_name=particle_name,i=intt)
        return {'FINISHED'}


class SCATTER_OT_slider_img_open_direct(bpy.types.Operator):
    bl_idname = "scatter.img_open_direct"
    bl_label = ""
    bl_description = "create an invert version of every texture in directory if not already there (you will need to refresh)"

    def execute(self, context):
        directory = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        filepath  = directory + '\\__textures__\\'
        os.startfile(filepath)
        return {'FINISHED'}

######################################################################################
# # # # # # # # # # # #          SLIDERS BATCH                # # # # # # # # # # # # 
######################################################################################

class SCATTER_OT_slider_batch_emi(bpy.types.Operator):
    bl_idname = "scatter.batch_emi"
    bl_label = ""
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].settings.count = addon_prefs.batch_emi
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_emisquare(bpy.types.Operator):
    bl_idname = "scatter.batch_emisquare"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bm = bmesh.new()
        bm.from_mesh(A.data) 
        squarearea = sum(f.calc_area() for f in bm.faces)
        bm.free()
        
        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    if addon_prefs.persquaremorkm == '/m²':
                        A.particle_systems[ob.name].settings.count =  addon_prefs.persquarem * squarearea
                    if addon_prefs.persquaremorkm == '/km²':
                        A.particle_systems[ob.name].settings.count =  addon_prefs.persquarem * (squarearea/1000)
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_seed(bpy.types.Operator):
    bl_idname = "scatter.batch_seed"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].seed = addon_prefs.batch_seed
        return {'FINISHED'}
    

class SCATTER_OT_slider_batch_seed_random(bpy.types.Operator):
    bl_idname = "scatter.batch_seed_random"
    bl_label = ""
    
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer
        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].seed = random.randint(0,10000)
        return {'FINISHED'}
    
###################################################################################### #Batch random scal

class SCATTER_OT_slider_batch_r_scale(bpy.types.Operator):
    bl_idname = "scatter.batch_r_scale"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].settings.size_random = addon_prefs.batch_r_scale
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_r_rot(bpy.types.Operator):
    bl_idname = "scatter.batch_r_rot"
    bl_label = ""

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].settings.phase_factor_random = addon_prefs.batch_r_rot
        return {'FINISHED'}


class SCATTER_OT_slider_batch_r_rot_tot(bpy.types.Operator):
    bl_idname = "scatter.batch_r_rot_random"
    bl_label = ""

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].settings.rotation_factor_random = addon_prefs.batch_r_rot_tot
        return {'FINISHED'}

    
###################################################################################### #Display

class SCATTER_OT_slider_batch_dis(bpy.types.Operator):
    bl_idname = "scatter.batch_dis"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    A.particle_systems[ob.name].settings.display_percentage = addon_prefs.batch_dis
        return {'FINISHED'}

###################################################################################### #Influence

class SCATTER_OT_slider_batch_t_idens(bpy.types.Operator):
    bl_idname = "scatter.batch_t_idens"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            slots.density_factor =addon_prefs.batch_t_idens
        return {'FINISHED'}
    

class SCATTER_OT_slider_batch_t_iscal(bpy.types.Operator):
    bl_idname = "scatter.batch_t_iscal"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            slots.length_factor =addon_prefs.batch_t_iscal
                                #A.particle_systems[ob.name].settings.texture_slots[slots.].length_factor =addon_prefs.batch_t_iscal
        return {'FINISHED'}

###################################################################################### #Colors

class SCATTER_OT_slider_batch_t_brigh(bpy.types.Operator):
    bl_idname = "scatter.batch_t_brigh"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            bpy.data.textures[slots.name].intensity = addon_prefs.batch_t_brigh
        return {'FINISHED'}

class SCATTER_OT_slider_batch_t_brigh_ran(bpy.types.Operator):
    bl_idname = "scatter.batch_t_brigh_ran"
    bl_label = ""
    
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            bpy.data.textures[slots.name].intensity = round(random.uniform(0.5,1.2),2) ###########
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_t_contr(bpy.types.Operator):
    bl_idname = "scatter.batch_t_contr"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            bpy.data.textures[slots.name].contrast = addon_prefs.batch_t_contr
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_t_contr_ran(bpy.types.Operator):
    bl_idname = "scatter.batch_t_contr_ran"
    bl_label = ""
    
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            bpy.data.textures[slots.name].contrast = round(random.uniform(0.9,3),2)
        return {'FINISHED'}

###################################################################################### #Batch Mapping

class SCATTER_OT_slider_batch_t_scal(bpy.types.Operator):
    bl_idname = "scatter.batch_t_scal"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            slots.scale.xyz =addon_prefs.batch_t_scal
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_t_scal_ran(bpy.types.Operator):
    bl_idname = "scatter.batch_t_scal_ran"
    bl_label = ""
    
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            slots.scale.xyz = round(random.uniform(0.01,1.7),2)
        return {'FINISHED'}


class SCATTER_OT_slider_batch_t_off(bpy.types.Operator):
    bl_idname = "scatter.batch_t_off"
    bl_label = ""
    
    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            slots.offset.xyz =addon_prefs.batch_t_off
        return {'FINISHED'}
    
class SCATTER_OT_slider_batch_t_off_ran(bpy.types.Operator):
    bl_idname = "scatter.batch_t_off_ran"
    bl_label = ""
    
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in A.particle_systems:
            if "SCATTER" in ob.name:
                if bpy.data.particles[ob.name]["is_selected"] == True:
                    for slots in A.particle_systems[ob.name].settings.texture_slots:
                        if slots != None:
                            slots.offset.xyz = round(random.uniform(-10,10),2)
        return {'FINISHED'}


######################################################################################
#  .oooooo.   ooooooooo.         .oooooo..o                         .         .o.                                       .
# d8P'  `Y8b  `888   `Y88.      d8P'    `Y8                       .o8        .888.                                    .o8
#888      888  888   .d88'      Y88bo.       .ooooo.   .oooo.   .o888oo     .8"888.      .oooo.o  .oooo.o  .ooooo.  .o888oo  .oooo.o
#888      888  888ooo88P'        `"Y8888o.  d88' `"Y8 `P  )88b    888      .8' `888.    d88(  "8 d88(  "8 d88' `88b   888   d88(  "8
#888      888  888                   `"Y88b 888        .oP"888    888     .88ooo8888.   `"Y88b.  `"Y88b.  888ooo888   888   `"Y88b.
#`88b    d88'  888              oo     .d8P 888   .o8 d8(  888    888 .  .8'     `888.  o.  )88b o.  )88b 888    .o   888 . o.  )88b
# `Y8bood8P'  o888o             8""88888P'  `Y8bod8P' `Y888""8o   "888" o88o     o8888o 8""888P' 8""888P' `Y8bod8P'   "888" 8""888P'

######################################################################################

class SCATTER_OT_collremove(bpy.types.Operator):
    bl_idname = "scatter.collremove"
    bl_label = ""
    bl_description = "remove from particles collection"
    obj_na : bpy.props.StringProperty() 
    def execute(self, context):
        obj_na = self.obj_na

        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer
        terrain_coll_name = "SCATTER: ["+A.name+"]"+" Particles"
        
        for p in A.particle_systems:
            if bpy.data.particles[p.name]["is_selected"]==1:
                nam=p.name
        
        for coll_child in bpy.data.collections[terrain_coll_name].children:
            if coll_child.name == nam: #active particle boolean (== ob)
                for obj in bpy.data.collections[coll_child.name].objects:
                    if obj.name == obj_na:
                        if obj.name not in bpy.context.scene.collection.objects:
                            bpy.context.scene.collection.objects.link(obj)
                        coll_child.objects.unlink(obj)
                    if obj.name == obj_na + " [proxy]":
                        if obj.name not in bpy.context.scene.collection.objects:
                            bpy.context.scene.collection.objects.link(obj)
                        coll_child.objects.unlink(obj)
        return {'FINISHED'}
    
    
class SCATTER_OT_colladd(bpy.types.Operator):
    bl_idname = "scatter.colladd"
    bl_label = ""
    bl_description = "add eye drop to particle collection"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer
        eyedrop = C_Slots.eye_dropper_prop
        
        for p in A.particle_systems:
            if bpy.data.particles[p.name]["is_selected"]==1:
                collection=bpy.data.collections[p.name]
        
        if eyedrop == None: return {'FINISHED'}

        if eyedrop.type != 'MESH':
            C_Slots.eye_dropper_prop = None
            ShowMessageBox("object type not appropriate", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        if eyedrop.name in collection.objects:
            C_Slots.eye_dropper_prop = None
            ShowMessageBox("object already in collection", "Be Careful" ,"ERROR")
            return {'FINISHED'}
        
        ob_old_coll = eyedrop.users_collection 
        for o in ob_old_coll:
            if "SCATTER:" not in o.name:
                o.objects.unlink(eyedrop)
                
        collection.objects.link(eyedrop)
        C_Slots.eye_dropper_prop = None
        return {'FINISHED'}

class SCATTER_OT_slider_is_bounds(bpy.types.Operator):
    bl_idname = "scatter.is_bounds"
    bl_label = ""
    bl_description = "toggle bounding boxes on/off"
    
    part_ob_name : bpy.props.StringProperty() 
    def execute(self, context):
        part_ob_name = self.part_ob_name

        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for obj in bpy.context.scene.objects:
            if obj.name == part_ob_name:
                if obj.display_type == 'BOUNDS':
                    obj.display_type = 'TEXTURED'
                else:
                    obj.display_type = 'BOUNDS'
        return {'FINISHED'}


class SCATTER_OT_selection_to_coll(bpy.types.Operator):
    bl_idname = "scatter.selection_to_coll"
    bl_label = ""
    bl_description = "use selection as particles"
    
    coll_name : bpy.props.StringProperty() 
    def execute(self, context):
        coll_name = self.coll_name

        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        for ob in bpy.context.selected_objects:
            if ob != A:
                if ob.type == 'MESH': coll_move_to_new(ob,coll_name)
        return {'FINISHED'}

def coll_move_to_new(ob,collname):
    new_coll_name = collname 
    if bpy.data.collections[new_coll_name]: new_coll = bpy.data.collections[new_coll_name]
    else: return
    ob_old_coll = ob.users_collection 
    for o in ob_old_coll : ob_old_coll = o #now have proper bpy struct
    ob_old_coll.objects.unlink(ob) ; new_coll.objects.link(ob)


######################################################################################
#  .oooooo.   ooooooooo.        ooooooooo.                                   o8o
# d8P'  `Y8b  `888   `Y88.      `888   `Y88.                                 `"'
#888      888  888   .d88'       888   .d88' oooo d8b  .ooooo.  oooo    ooo oooo   .ooooo.   .oooo.o
#888      888  888ooo88P'        888ooo88P'  `888""8P d88' `88b  `88b..8P'  `888  d88' `88b d88(  "8
#888      888  888               888          888     888   888    Y888'     888  888ooo888 `"Y88b.
#`88b    d88'  888               888          888     888   888  .o8"'88b    888  888    .o o.  )88b
# `Y8bood8P'  o888o             o888o        d888b    `Y8bod8P' o88'   888o o888o `Y8bod8P' 8""888P'
#
######################################################################################

class SCATTER_OT_set_up_proxy(bpy.types.Operator):
    bl_idname = "scatter.set_up_proxy"
    bl_label = ""
    bl_description = "Set-Up/Update a proxy system"
    def execute(self, context):

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer
        ps = Terrain.particle_systems
        terrain_coll_name = "SCATTER: ["+Terrain.name+"]"+" Particles"
        obj_list = []

        if Terrain:
            for ob in ps: #i need to make sure proxy order = same than obj order 
                if bpy.data.particles[ob.name]["is_selected"]==1:
                    
                    #remove viewport because better performance ###################################
                    #Terrain.modifiers[ob.name].show_viewport = False

                    override = {"object": Terrain, "particle_system": ob, } #remove already slots to renew them.
                    for i in range(len(ob.settings.instance_weights)): bpy.ops.particle.dupliob_remove(override) #; bpy.ops.particle.dupliob_refresh(override)

                    for coll in bpy.context.scene.collection.children:
                        if coll.name == terrain_coll_name:
                            for coll_child in bpy.data.collections[terrain_coll_name].children:
                                if coll_child.name == ob.name:

                                    if len(coll_child.objects) %2!=0: #check if pair; if impair then abort
                                        ShowMessageBox("Have one proxy per scattered assets", "Be Careful" ,"ERROR")
                                        return {'FINISHED'}

                                    prox_list = [] #check if 50/50, else = abort
                                    not_prox_list = []
                                    for obj in coll_child.objects:
                                        if 'proxy' in obj.name: prox_list.append(obj.name)
                                        if 'proxy' not in obj.name: not_prox_list.append(obj.name)
                                    if len(prox_list) != len(not_prox_list):
                                        ShowMessageBox("Have one proxy per scattered assets", "Be Careful" ,"ERROR")
                                        return {'FINISHED'}

                                    if len(prox_list) == len(not_prox_list): 
                                        for obj in coll_child.objects:
                                            if obj.name not in bpy.context.scene.collection.objects:
                                                bpy.context.scene.collection.objects.link(obj)
                                            coll_child.objects.unlink(obj)
                                            obj_list.append(obj.name)
                    
                                        obj_list.sort() #Sort list so right order !!!
                                        for obj in obj_list: coll_child.objects.link(bpy.data.objects[obj])
                                            
                                        for obj in bpy.context.scene.collection.objects:
                                            if obj.name in obj_list:
                                                bpy.context.scene.collection.objects.unlink(obj)
                                        Terrain.modifiers[ob.name].particle_system.settings.use_collection_count = False
                                        Terrain.modifiers[ob.name].particle_system.settings.use_collection_count = True

                    for iw in ps[ob.name].settings.instance_weights:
                        if "[proxy]" in iw.name: iw.count =1
                        else: iw.count =0
                        bpy.data.particles[ob.name]["is_proxy"]=1
                        Terrain.modifiers[ob.name].particle_system.settings.use_collection_count = False
                        Terrain.modifiers[ob.name].particle_system.settings.use_collection_count = True

                    #remove viewport because better performance
                    #Terrain.modifiers[ob.name].show_viewport = True

        if 'is_timer_on' not in bpy.context.scene: bpy.context.scene['is_timer_on']='OFF'
        return {'FINISHED'}

class SCATTER_OT_toggle_proxy(bpy.types.Operator):
    bl_idname = "scatter.toggle_proxy"
    bl_label = ""
    bl_description = "Toggle the proxy system"
    def execute(self, context):
        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer
        ps = Terrain.particle_systems
        if Terrain:
            for ob in ps:
                if bpy.data.particles[ob.name]["is_selected"]==1:
                    for iw in ps[ob.name].settings.instance_weights:
                        if iw.count ==0: iw.count =1
                        else: iw.count =0
                    if bpy.data.particles[ob.name]["is_proxy"]==1: bpy.data.particles[ob.name]["is_proxy"]=0
                    else: bpy.data.particles[ob.name]["is_proxy"]=1
        return {'FINISHED'}

######################################################################################
def proxy_scene_on():
    for asset in bpy.context.scene.objects:
        if asset.type == 'MESH':
            for ps in asset.particle_systems:
                if 'SCATTER' in ps.name:
                    if 'is_proxy' in ps.settings:
                        if ps.settings['is_proxy'] == 0:
                            for iw in ps.settings.instance_weights:
                                if iw.count ==0: iw.count =1
                                else: iw.count =0
                                ps.settings["is_proxy"]=1
def proxy_scene_off():
    for asset in bpy.context.scene.objects:
        if asset.type == 'MESH':
            for ps in asset.particle_systems:
                if 'SCATTER' in ps.name:
                    if 'is_proxy' in ps.settings:
                        if ps.settings['is_proxy'] == 1:
                            for iw in ps.settings.instance_weights:
                                if iw.count ==0: iw.count =1
                                else: iw.count =0
                                ps.settings["is_proxy"]=0
@persistent
def pre(scene):
    if 'not_twice_final_pre' not in bpy.context.scene: #system to make sure don't toggle on twice in a row because user reg/unreg incorrectly. 
        bpy.context.scene['not_twice_final_pre']=0
    bpy.context.scene['not_twice_final_post']=0
    if bpy.context.scene['not_twice_final_pre']==0:
        bpy.context.scene['not_twice_final_pre']+=1
        #print("all scene proxies off")
        proxy_scene_off()

@persistent
def post(scene):
    if bpy.context.scene['not_twice_final_post']==0:
        bpy.context.scene['not_twice_final_post']+=1
        bpy.context.scene['not_twice_final_pre']=0
        #print("all scene proxies on")
        proxy_scene_on()
 
def every_x_seconds(): #TIMER
    if bpy.context.scene['is_timer_on']=='OFF':
        #print('timer aborted')
        return None
    for area in bpy.data.screens[bpy.context.scene['context_screen']].areas:
        for space in area.spaces: 
            if space.type == 'VIEW_3D':
                if space.shading.type == 'RENDERED':
                    space.overlay.show_overlays = False
                    if bpy.context.preferences.addons[__name__].preferences.scatter_always_hund == True:
                        for ps in bpy.data.objects[bpy.context.scene['context_obj']].particle_systems:
                            bpy.data.particles[ps.name]["display_perc"] = ps.settings.display_percentage
                            ps.settings.display_percentage = 100
                    proxy_scene_off()
                    #print("proxies off, starting new timer")
                    bpy.app.timers.register(functools.partial(check_if_not_rendered, space), first_interval=1.0)
                    return None
    #print('check for rendered')
    return 0.5

def check_if_not_rendered(message): #TIMER
    if message.shading.type != 'RENDERED':
        message.overlay.show_overlays = True
        proxy_scene_on()
        if bpy.context.preferences.addons[__name__].preferences.scatter_always_hund == True:
            for ps in bpy.data.objects[bpy.context.scene['context_obj']].particle_systems:
                if "display_perc" in bpy.data.particles[ps.name]:
                    ps.settings.display_percentage = bpy.data.particles[ps.name]["display_perc"]
        #print("proxies on, starting new timer")
        bpy.app.timers.register(every_x_seconds)
        return None
    #print('check if rendered')
    return 0.2

######################################################################################

class SCATTER_OT_toggle_proxy_all(bpy.types.Operator):
    bl_idname = "scatter.toggle_proxy_all"
    bl_label = ""
    bl_description = ""
    def execute(self, context):
        if 'is_proxy_all' not in bpy.context.scene:
            bpy.context.scene['is_proxy_all']=0
        bpy.context.scene['is_proxy_all']+=1
        if bpy.context.scene['is_proxy_all']%2!=0:
            proxy_scene_off()
        else: proxy_scene_on()
        return {'FINISHED'}
######################################################################################

class SCATTER_OT_listen_to_view(bpy.types.Operator):
    bl_idname = "scatter.listen_to_view"
    bl_label = ""
    bl_description = ""
    def execute(self, context):
        if "is_timer_on" not in bpy.context.scene:
            bpy.context.scene['is_timer_on']='OFF'

        if bpy.context.scene['is_timer_on']=='OFF':
            bpy.context.scene['is_timer_on']='ON'
            bpy.context.scene['context_screen'] = bpy.context.screen.name
            bpy.context.scene['context_obj']    = bpy.context.object.name
            bpy.app.timers.register(every_x_seconds)
        else:
            bpy.context.scene['is_timer_on']='OFF'
        
        return {'FINISHED'}

######################################################################################
#  .oooooo.   ooooooooo.        ooooooooo.              o8o                  .    o8o
# d8P'  `Y8b  `888   `Y88.      `888   `Y88.            `"'                .o8    `"'
#888      888  888   .d88'       888   .d88'  .oooo.   oooo  ooo. .oo.   .o888oo oooo  ooo. .oo.    .oooooooo
#888      888  888ooo88P'        888ooo88P'  `P  )88b  `888  `888P"Y88b    888   `888  `888P"Y88b  888' `88b
#888      888  888               888          .oP"888   888   888   888    888    888   888   888  888   888
#`88b    d88'  888               888         d8(  888   888   888   888    888 .  888   888   888  `88bod8P'
# `Y8bood8P'  o888o             o888o        `Y888""8o o888o o888o o888o   "888" o888o o888o o888o `8oooooo.
#                                                                                                  d"     YD
#                                                                                                  "Y88888P'
######################################################################################


class SCATTER_OT_paint(bpy.types.Operator):
    bl_idname = "scatter.paint"
    bl_label = ""
    bl_description = ""
    def execute(self, context):

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        if len(Terrain.data.polygons) < 150:
            ShowMessageBox("Your terrain don't have enough geometry for the weight proximity modifier", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        if "paint_index" not in bpy.context.scene: bpy.context.scene["paint_index"] = 0

        i = 0
        for v in Terrain.vertex_groups:
            if "PAINT" in v.name: i+=1
        if i == 0: bpy.context.scene["paint_index"] = 0

        bpy.context.scene["paint_index"] += 1 

        layer = "PAINT" + str(bpy.context.scene["paint_index"])
        if layer not in Terrain.vertex_groups:

            A = bpy.context.object
            S = bpy.context.selected_objects
            for o in S: o.select_set(state=False)
            bpy.context.view_layer.objects.active = C_Slots.Terrain_pointer
            C_Slots.Terrain_pointer.select_set(state=True)

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT') #'DESELECT'
            bpy.ops.object.vertex_group_add()
            bpy.context.object.vertex_groups[len(Terrain.vertex_groups)-1].name = layer
            bpy.context.scene.tool_settings.vertex_group_weight = 0     
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()

            C_Slots.Terrain_pointer.select_set(state=False)
            bpy.context.view_layer.objects.active = A
            for o in S: o.select_set(state=True)

        bpy.context.scene[layer] = layer
        return {'FINISHED'}



class SCATTER_OT_paint_del(bpy.types.Operator):
    bl_idname = "scatter.paint_del"
    bl_label = ""
    bl_description = ""

    paint_layer : bpy.props.StringProperty()
    def execute(self, context):
        paint_layer = self.paint_layer

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = C_Slots.Terrain_pointer
        C_Slots.Terrain_pointer.select_set(state=True)

        for v in Terrain.vertex_groups:
            if v.name == paint_layer:
                bpy.ops.object.vertex_group_set_active(group=v.name)
                bpy.ops.object.vertex_group_remove(all=False, all_unlocked=False)

        for m in Terrain.modifiers:
            if paint_layer in m.name[:9]:
                bpy.ops.object.modifier_remove(modifier=m.name)

        C_Slots.Terrain_pointer.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'}

class SCATTER_OT_paint_infl_rem(bpy.types.Operator):
    bl_idname = "scatter.paint_infl_rem"
    bl_label = ""
    bl_description = ""

    concerned_m : bpy.props.StringProperty()
    def execute(self, context):
        concerned_m = self.concerned_m

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = C_Slots.Terrain_pointer
        C_Slots.Terrain_pointer.select_set(state=True)

        for m in Terrain.modifiers:
            if m.name == concerned_m:
                bpy.ops.object.modifier_remove(modifier=m.name)

        C_Slots.Terrain_pointer.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'}


class SCATTER_OT_paint_show(bpy.types.Operator):
    bl_idname = "scatter.paint_show"
    bl_label = ""
    bl_description = ""

    concerned_m : bpy.props.StringProperty()
    def execute(self, context):
        concerned_m = self.concerned_m

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        for m in Terrain.modifiers:
            if m.name == concerned_m:
                if m.show_viewport == True: m.show_viewport = False ; m.show_render   = False
                else: m.show_viewport = True ; m.show_render   = True
        return {'FINISHED'}


class SCATTER_OT_paint_part_infl(bpy.types.Operator):
    bl_idname = "scatter.paint_part_infl"
    bl_label = ""
    bl_description = ""

    paint_layer : bpy.props.StringProperty()
    def execute(self, context):
        paint_layer = self.paint_layer

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = C_Slots.Terrain_pointer
        C_Slots.Terrain_pointer.select_set(state=True)

        for p in Terrain.particle_systems:
            if "SCATTER" in p.name:
                if bpy.data.particles[p.name]["is_selected"] == True:
                    paint_mix = paint_layer + ":" + p.name[9:]
                    if paint_mix not in Terrain.modifiers:
                        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                        Terrain.modifiers[len(Terrain.modifiers)-1].name = paint_mix

                        Terrain.modifiers[paint_mix].vertex_group_a    = p.name
                        Terrain.modifiers[paint_mix].default_weight_b  = 1
                        Terrain.modifiers[paint_mix].mask_vertex_group = paint_layer
                        Terrain.modifiers[paint_mix].mix_mode = 'SUB'
                        Terrain.modifiers[paint_mix].mix_set  = 'A'
                        Terrain.modifiers[paint_mix].show_expanded = False
                        Terrain.modifiers[paint_mix].show_viewport = True #let user choose
                        Terrain.modifiers[paint_mix].show_render   = True

                        #Modifiers at right place, always above
                        m = Terrain.modifiers
                        if "CAM-CUT: Camera-Clip" in m:
                            for i in range(9999):
                                if m[i].name == "CAM-CUT: Camera-Clip": break
                        else:
                            for i in range(9999):
                                if m[i].type == 'PARTICLE_SYSTEM': i=i ; break
                        while m[i].name != paint_mix: bpy.ops.object.modifier_move_up(modifier=paint_mix)
                    else: ShowMessageBox("Selected System Already under influence", "Info",'ERROR')

        C_Slots.Terrain_pointer.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        bpy.ops.scatter.inverseinfluence(just_create=True, of_this_one="")
        return {'FINISHED'}



class SCATTER_OT_paint_go_in_weight(bpy.types.Operator):
    bl_idname = "scatter.paint_go_in_weight"
    bl_label = ""
    bl_description = "start painting"

    paint_layer : bpy.props.StringProperty()
    def execute(self, context):
        paint_layer = self.paint_layer

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        for v in Terrain.vertex_groups:
            if v.name == paint_layer:
                bpy.ops.object.vertex_group_set_active(group=v.name)
        bpy.ops.paint.weight_paint_toggle()
        bpy.context.scene.tool_settings.unified_paint_settings.weight = 1
        return {'FINISHED'}

class SCATTER_OT_paint_invert(bpy.types.Operator):
    bl_idname = "scatter.paint_invert"
    bl_label = ""
    bl_description = "inverse vgroup"

    paint_layer : bpy.props.StringProperty()
    def execute(self, context):
        paint_layer = self.paint_layer

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        for o in bpy.context.selected_objects:
            if o!= Terrain: o.select_set(state=False)
            
        for v in Terrain.vertex_groups:
            if v.name == paint_layer:
                bpy.ops.object.vertex_group_set_active(group=v.name)
        bpy.ops.paint.weight_paint_toggle()
        bpy.ops.object.vertex_group_invert()
        bpy.ops.paint.weight_paint_toggle()

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'}

class SCATTER_OT_paint_clear(bpy.types.Operator):
    bl_idname = "scatter.paint_clear"
    bl_label = ""
    bl_description = "clear vgroup"

    paint_layer : bpy.props.StringProperty()
    def execute(self, context):
        paint_layer = self.paint_layer

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        for o in bpy.context.selected_objects:
            if o!= Terrain: o.select_set(state=False)
            
        for v in Terrain.vertex_groups:
            if v.name == paint_layer:
                bpy.ops.object.vertex_group_set_active(group=v.name)
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT') #'DESELECT'
        bpy.context.scene.tool_settings.vertex_group_weight = 0 
        bpy.ops.object.vertex_group_assign()    
        bpy.ops.object.editmode_toggle()

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)
        return {'FINISHED'}


class SCATTER_OT_add_remove(bpy.types.Operator):
    bl_idname = "scatter.add_remove"
    bl_label = ""
    bl_description = "add/remove particles toggle"

    concerned_m : bpy.props.StringProperty()
    def execute(self, context):
        concerned_m = self.concerned_m

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        for m in Terrain.modifiers:
            if m.name == concerned_m:
                if m.mix_mode == 'ADD'   :  m.mix_mode = 'SUB'
                elif m.mix_mode == 'SUB' :  m.mix_mode = 'ADD'
        return {'FINISHED'}


######################################################################################
#
#  .oooooo.   ooooooooo.        oooooooooo.                      oooo
# d8P'  `Y8b  `888   `Y88.      `888'   `Y8b                     `888
#888      888  888   .d88'       888     888  .ooooo.   .ooooo.   888   .ooooo.   .oooo.   ooo. .oo.
#888      888  888ooo88P'        888oooo888' d88' `88b d88' `88b  888  d88' `88b `P  )88b  `888P"Y88b
#888      888  888               888    `88b 888   888 888   888  888  888ooo888  .oP"888   888   888
#`88b    d88'  888               888    .88P 888   888 888   888  888  888    .o d8(  888   888   888
# `Y8bood8P'  o888o             o888bood8P'  `Y8bod8P' `Y8bod8P' o888o `Y8bod8P' `Y888""8o o888o o888o
#
######################################################################################

class SCATTER_OT_Bool_Path(bpy.types.Operator): #main boolean operator
    bl_idname = "scatter.bool_path"
    bl_label = "Particles Boolean Operator"
    bl_description = ""

    def execute(self, context):
        context = bpy.context
        addon_prefs = context.preferences.addons[__name__].preferences

        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        scene = context.scene
        Selection=bpy.context.selected_objects

        if len(A.data.polygons) < 150:
            ShowMessageBox("Your terrain don't have enough geometry for the weight proximity modifier", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        NUM=1
        A.select_set(state=False)
        for Curve in bpy.context.selected_objects:
            if Curve.type != 'CURVE':
                Curve.select_set(state=False)
            else:
                NUM=NUM+1
                bpy.context.view_layer.objects.active = Curve
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                if Curve.data.splines[-1].use_cyclic_u ==True:
                    if 'EdgeSplit' not in Curve.modifiers:
                        if 'Solidify' in Curve.modifiers:
                            bpy.ops.object.modifier_remove(modifier="Solidify")
                        Curve.data.dimensions = '2D'
                        Curve.data.extrude = 0
                        Curve.data.splines[-1].use_cyclic_u = True
                        Curve.data.fill_mode = 'FRONT'
                        Curve.display_type = 'WIRE'

                        Curve.hide_render = True
                        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                        Curve.modifiers["EdgeSplit"].split_angle = 0
                        bpy.ops.object.modifier_add(type='SOLIDIFY')
                        Curve.modifiers["Solidify"].thickness = 3
                        Curve.modifiers["Solidify"].offset = 0

                else:
                    if 'Solidify' not in Curve.modifiers:
                        Curve.display_type = 'WIRE'
                        Curve.hide_render = True
                        Curve.data.extrude = 0.1
                        bpy.ops.object.modifier_add(type='SOLIDIFY')
                        Curve.modifiers['Solidify'].thickness = 0
                        
                cy = Curve.cycles_visibility
                if cy.camera != False: cy.camera=cy.diffuse=cy.glossy=cy.transmission=cy.scatter=cy.shadow=False

                if "tab_open" not in bpy.data.objects[Curve.name]:
                    bpy.data.objects[Curve.name]["tab_open"] = True

                bpy.context.view_layer.objects.active = A
                for p in A.particle_systems:
                    if "SCATTER" in p.name:
                        modifname="BOOL:["+Curve.name+"]" + p.name[9:]
                        if modifname not in A.modifiers:
                            if bpy.data.particles[p.name]["is_selected"] == True:
                                bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_PROXIMITY')
                                A.modifiers[len(A.modifiers)-1].name = modifname
                                A.modifiers[modifname].show_viewport = False #perf?
                                A.modifiers[modifname].target = Curve
                                A.modifiers[modifname].vertex_group = p.name
                                A.modifiers[modifname].mask_vertex_group = p.name
                                A.modifiers[modifname].proximity_mode = 'GEOMETRY'
                                A.modifiers[modifname].proximity_geometry = {'FACE'}
                                A.modifiers[modifname].min_dist = addon_prefs.batch_curve_dist - (addon_prefs.batch_curve_falloff/2)
                                A.modifiers[modifname].max_dist = addon_prefs.batch_curve_dist + (addon_prefs.batch_curve_falloff/2)

                                A.modifiers[modifname].show_expanded = False
                                while A.modifiers[0].name != modifname: bpy.ops.object.modifier_move_up(modifier=modifname) #top_the_top!
                                A.modifiers[modifname].show_viewport = True #perf?

        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        bpy.ops.scatter.inverseinfluence(just_create=True, of_this_one="")

        return {'FINISHED'}

class SCATTER_OT_bool_add_inlfe(bpy.types.Operator): #main boolean operator
    bl_idname = "scatter.bool_add_inlfe"
    bl_label = "add boolean influence to the selected particle system"
    bl_description = ""

    curve_na : bpy.props.StringProperty()
    def execute(self, context):
        curve_na = self.curve_na

        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        Active = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        A.select_set(state=True)

        for p in A.particle_systems:
            if bpy.data.particles[p.name]["is_selected"] == True:
                modifname="BOOL:"+"["+curve_na+"]"+p.name[9:]
                if modifname not in A.modifiers:
                    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_PROXIMITY')
                    A.modifiers[len(A.modifiers)-1].name = modifname
                    A.modifiers[len(A.modifiers)-1].target = bpy.data.objects[curve_na]
                    A.modifiers[len(A.modifiers)-1].vertex_group = p.name
                    A.modifiers[len(A.modifiers)-1].mask_vertex_group = p.name
                    A.modifiers[len(A.modifiers)-1].proximity_mode = 'GEOMETRY'
                    A.modifiers[len(A.modifiers)-1].proximity_geometry = {'FACE'}
                    A.modifiers[len(A.modifiers)-1].min_dist = addon_prefs.batch_curve_dist - (addon_prefs.batch_curve_falloff/2)
                    A.modifiers[len(A.modifiers)-1].max_dist = addon_prefs.batch_curve_dist + (addon_prefs.batch_curve_falloff/2)
                    A.modifiers[len(A.modifiers)-1].show_expanded = False

                    while A.modifiers[0].name != modifname: bpy.ops.object.modifier_move_up(modifier=modifname) #top the top !

        A.select_set(state=False)
        bpy.context.view_layer.objects.active = Active
        for o in S: o.select_set(state=True)

        return {'FINISHED'}

class SCATTER_OT_bool_open_min_tab(bpy.types.Operator): #main boolean operator
    bl_idname = "scatter.bool_open_min_tab"
    bl_label = "open tab"
    bl_description = ""

    cuname : bpy.props.StringProperty()
    def execute(self, context):
        cuname = self.cuname
        if bpy.data.objects[cuname]["tab_open"] == True:
            bpy.data.objects[cuname]["tab_open"] = False
        else: bpy.data.objects[cuname]["tab_open"] = True
        return {'FINISHED'}


class SCATTER_OT_inverseinfluence(bpy.types.Operator):
    bl_idname = "scatter.inverseinfluence"
    bl_label = "invert system vgroup"
    bl_description = "inverse vgroups of this particle system"

    just_create : bpy.props.BoolProperty()
    of_this_one : bpy.props.StringProperty()
    def execute(self, context):
        just_create = self.just_create
        of_this_one = self.of_this_one

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        if of_this_one == "":
            for p in Terrain.particle_systems:
                if "SCATTER" in p.name:
                    modifnamemix ="INVERT:"+p.name[9:] #Create if not already here
                    if modifnamemix not in Terrain.modifiers:
                        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                        Terrain.modifiers[len(Terrain.modifiers)-1].name             = modifnamemix
                        Terrain.modifiers[len(Terrain.modifiers)-1].mix_mode         = 'DIF'
                        Terrain.modifiers[len(Terrain.modifiers)-1].mix_set          = 'A'
                        Terrain.modifiers[len(Terrain.modifiers)-1].default_weight_b = 1
                        Terrain.modifiers[len(Terrain.modifiers)-1].vertex_group_a   = p.name
                        Terrain.modifiers[len(Terrain.modifiers)-1].show_expanded    = False
                        Terrain.modifiers[len(Terrain.modifiers)-1].show_viewport    = False
                        Terrain.modifiers[len(Terrain.modifiers)-1].show_render      = False

                        #Modifiers at right place, always above
                        m = Terrain.modifiers
                        is_paint=False
                        for mod in m:
                            if mod.name[:5] == "PAINT": is_paint=True #if paint layer then always above paint
                        if is_paint==True:
                            for i in range(9999):
                                if m[i].name[:5] == "PAINT": break
                        elif "CAM-CUT: Camera-Clip" in m: #if not paint but cam set up always above cam
                            for i in range(9999):
                                if m[i].name == "CAM-CUT: Camera-Clip": break
                        else: #if not paint and not cam then always above particles
                            for i in range(9999):
                                if m[i].type == 'PARTICLE_SYSTEM': i=i ; break
                        while m[i].name != modifnamemix: bpy.ops.object.modifier_move_up(modifier=modifnamemix)

                    if just_create == False:
                        for m in Terrain.modifiers:
                            if "INVERT" in m.name:
                                if p.name[9:] == m.name[-len(p.name[9:]):]:
                                    if m.show_viewport == True: m.show_viewport = m.show_render = False #toggle
                                    else: m.show_viewport = m.show_render = True                        #toggle
        else:
            for m in Terrain.modifiers:
                if "INVERT" in m.name:
                    if m.name[7:] == of_this_one:
                        if m.show_viewport == True: m.show_viewport = m.show_render = False #toggle
                        else: m.show_viewport = m.show_render = True                        #toggle

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'}


class SCATTER_OT_activeisname(bpy.types.Operator): #select curve
    bl_idname = "scatter.activeisname"
    bl_label = ""
    bl_description = "select curve"
    futureactivename : bpy.props.StringProperty()
    def execute(self, context):
        futureactivename = self.futureactivename
        A = bpy.context.object
        for sel in bpy.context.selected_objects:
            if sel !=A:
                if sel.type != 'CURVE':
                    sel.select_set(state=False)
        for ob in bpy.context.scene.objects:
            if ob.name == futureactivename:
                if ob in bpy.context.selected_objects:
                    ob.select_set(state=False)
                else: ob.select_set(state=True)
        return {'FINISHED'}

class SCATTER_OT_hidecurve(bpy.types.Operator):
    bl_idname = "scatter.hidecurve"
    bl_label = ""
    bl_description = "hide/show all curves influence"
    tobehidden : bpy.props.StringProperty() 
    def execute(self, context):
        tobehidden = self.tobehidden
        if "true_or_false" not in bpy.context.scene:
            bpy.context.scene["true_or_false"]=False
        verdict = bpy.context.scene["true_or_false"]

        C_Slots = bpy.context.scene.C_Slots_settings
        A = C_Slots.Terrain_pointer

        lista = "what"
        for m in A.modifiers:
            if "BOOL" in m.name:
                if m.target.name == tobehidden:
                    m.show_render   = verdict
                    m.show_viewport = verdict
                    if verdict == True: bpy.context.scene["true_or_false"]=False
                    else: bpy.context.scene["true_or_false"]=True
        return {'FINISHED'}

class SCATTER_OT_destroycurve(bpy.types.Operator):
    bl_idname = "scatter.destroycurve"
    bl_label = ""
    bl_description = "remove influence from all particles systems"
    futureactivename : bpy.props.StringProperty()
    def execute(self, context):
        futureactivename = self.futureactivename

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        for m in Terrain.modifiers:
            if "BOOL" in m.name:
                if m.target.name == futureactivename:
                    bpy.ops.object.modifier_remove(modifier=m.name)
        del bpy.data.objects[futureactivename]["tab_open"]

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'}

class SCATTER_OT_removecurve(bpy.types.Operator):
    bl_idname = "scatter.removecurve"
    bl_label = ""
    bl_description = "remove influence from selected particles systems"
    futureactivename : bpy.props.StringProperty()
    def execute(self, context):
        futureactivename = self.futureactivename

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        for p in Terrain.particle_systems:
            if "SCATTER" in p.name:
                if bpy.data.particles[p.name]["is_selected"]==1:
                    p_sys = p
        for m in Terrain.modifiers:
            if "BOOL" in m.name:
                if p_sys.name[9:] == m.name[-len(p.name[9:]):]:
                    if m.target.name == futureactivename:
                        bpy.ops.object.modifier_remove(modifier=m.name)

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'}

class SCATTER_OT_curvesliderinfluence(bpy.types.Operator):
    bl_idname = "scatter.curvesliderinfluence"
    bl_label = ""
    bl_description = "inverse the boolean infuence for the selected particle system"
    curvenamee : bpy.props.StringProperty() 
    def execute(self, context):
        curvenamee = self.curvenamee
        n =0
        for c in bpy.context.selected_objects:
            if c.type == "CURVE":
                n+=1
        if n==0: return {'FINISHED'}

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        addon_prefs = bpy.context.preferences.addons[__name__].preferences

        for c in bpy.context.selected_objects:
            if c.type == "CURVE":
                curvenamee = c.name
                for m in Terrain.modifiers:
                    if 'BOOL' in m.name:
                        if m.name[5:len(curvenamee)+7] == "["+curvenamee+"]":
                            m.min_dist = addon_prefs.batch_curve_dist - (addon_prefs.batch_curve_falloff/2)
                            m.max_dist = addon_prefs.batch_curve_dist + (addon_prefs.batch_curve_falloff/2)
                            m.mask_constant = addon_prefs.batch_curve_infl

        return {'FINISHED'}

######################################################################################
#  .oooooo.   ooooooooo.          .oooooo.
# d8P'  `Y8b  `888   `Y88.       d8P'  `Y8b
#888      888  888   .d88'      888           .oooo.   ooo. .oo.  .oo.    .ooooo.  oooo d8b  .oooo.
#888      888  888ooo88P'       888          `P  )88b  `888P"Y88bP"Y88b  d88' `88b `888""8P `P  )88b
#888      888  888              888           .oP"888   888   888   888  888ooo888  888      .oP"888
#`88b    d88'  888              `88b    ooo  d8(  888   888   888   888  888    .o  888     d8(  888
# `Y8bood8P'  o888o              `Y8bood8P'  `Y888""8o o888o o888o o888o `Y8bod8P' d888b    `Y888""8o
#
######################################################################################


class SCATTER_OT_camera_crop_and_density(bpy.types.Operator):
    bl_idname = "scatter.camera_crop_and_density"
    bl_label = ""
    bl_description = "Create or Update A camera clipping and proximity mask."

    def execute(self, context):
        C = bpy.context
        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        if len(Terrain.data.polygons) < 150:
            ShowMessageBox("Your terrain don't have enough geometry for the weight proximity modifier", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        deleted_scalex ,deleted_scaley,deleted_scalez = 1,1,1
        for ob in C.scene.objects: #need to redo cam as fov can change, activ can can change
            if ob.name =="CAM-CUT: Camera-Clip":
                deleted_scalex,deleted_scaley,deleted_scalez = ob.scale.x,ob.scale.y,ob.scale.z
                bpy.data.objects.remove(ob, do_unlink=True)

        if C.scene.camera == None:
            bpy.ops.object.camera_add(align='VIEW',location=(0,0,0),rotation=(1.5708,0,0))
            C.scene.camera = C.view_layer.objects.active

        CAM     = C.scene.camera
        C.view_layer.objects.active = CAM
        FOV  = C.object.data.angle
        Vcam = "CAM-CUT: Camera-Clip"
        int=0

        #remove viewport because better performance ###################################
        partviewporttrue = []
        for p in Terrain.particle_systems:
            if "SCATTER" in p.name:
                if Terrain.modifiers[p.name].show_viewport == True:
                    partviewporttrue.append(p.name)
                    Terrain.modifiers[p.name].show_viewport = False
        #print(partviewporttrue)

        #Cam Crop Part ###################################

        C.scene.cursor.location = CAM.location
        bpy.ops.mesh.primitive_cube_add(size=2)
        BOOL = C.object
        BOOL.rotation_euler=CAM.rotation_euler
        BOOL.name = BOOL.data.name = Vcam
        BOOL.display_type = 'WIRE'
        BOOL.hide_render = True
        cy=BOOL.cycles_visibility ;cy.camera=cy.transmission=cy.diffuse=cy.scatter=cy.glossy=cy.shadow= False

        terrain_coll_name = "SCATTER: ["+Terrain.name+"]"+" Particles"
        if terrain_coll_name not in bpy.data.collections:
          terrain_coll = bpy.data.collections.new(name=terrain_coll_name)
          bpy.context.scene.collection.children.link(terrain_coll)
        else: terrain_coll = bpy.data.collections[terrain_coll_name]
        if Vcam not in bpy.data.collections:
            brush_coll = bpy.data.collections.new(name=Vcam)
            bpy.data.collections[terrain_coll_name].children.link(brush_coll)
        else: brush_coll = bpy.data.collections[Vcam]
        bool_old_coll = BOOL.users_collection 
        for o in bool_old_coll : bool_old_coll = o #now have proper bpy struct
        bool_old_coll.objects.unlink(BOOL)
        brush_coll.objects.link(BOOL)

        C.view_layer.objects.active = BOOL
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        mesh = bmesh.from_edit_mesh(BOOL.data)
        for f in mesh.faces:
            if f.index ==5: f.select = True
        bpy.ops.mesh.select_mode(type='EDGE') ; bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.merge(type='CURSOR')
        bpy.ops.object.editmode_toggle()

        bpy.ops.object.transform_apply(location=0,rotation=0,scale=1)#=FFT
        C.object.scale[2] = 1/math.tan(FOV/2)

        CAM.select_set(state=True)
        C.view_layer.objects.active = CAM
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        for i in range(3): BOOL.lock_rotation[i] = BOOL.lock_location[i] = True

        dimension_x , dimension_y = C.scene.render.resolution_x /1000 , C.scene.render.resolution_y /1000
        BOOL.dimensions.xy = (dimension_x,dimension_y) #to get correct ratio
        if dimension_x>dimension_y:
            divider = 2/dimension_x
        else: divider = 2/dimension_y
        BOOL.scale.xy = (BOOL.scale.x*divider,BOOL.scale.y*divider)
        for i in range(3): BOOL.scale[i] = BOOL.scale[i] *100
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True) #give xyz sacel access to public.
        BOOL.scale.xyz = (deleted_scalex,deleted_scaley,deleted_scalez) #vector = vector directly didn't work, strange..

        C.view_layer.objects.active = BOOL
        BOOL.select_set(state=True)
        if Vcam not in BOOL.modifiers:
            bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
            BOOL.modifiers[len(BOOL.modifiers)-1].name = Vcam
            BOOL.modifiers[Vcam].ui_type = 'BRUSH'
            bpy.ops.dpaint.type_toggle(type='BRUSH')
            BOOL.modifiers[Vcam].brush_settings.paint_source = 'VOLUME'  
            BOOL.modifiers[Vcam].show_expanded = False

        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True) ; BOOL.select_set(state=False) ; CAM.select_set(state=False)

        if Vcam not in Terrain.vertex_groups:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT') #'DESELECT'
            bpy.ops.object.vertex_group_add()
            bpy.context.object.vertex_groups[len(Terrain.vertex_groups)-1].name = Vcam
            bpy.context.scene.tool_settings.vertex_group_weight = 1
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()

        if Vcam not in Terrain.modifiers:
            bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
            Terrain.modifiers[len(Terrain.modifiers)-1].name = Vcam
            bpy.ops.dpaint.type_toggle(type='CANVAS')
            Terrain.modifiers[Vcam].canvas_settings.canvas_surfaces["Surface"].surface_type = 'WEIGHT'
            Terrain.modifiers[Vcam].canvas_settings.canvas_surfaces["Surface"].output_name_a = Vcam
            Terrain.modifiers[Vcam].canvas_settings.canvas_surfaces["Surface"].brush_collection = brush_coll
            Terrain.modifiers[Vcam].show_expanded = False
            int+=1

        if "CAM-CUT: Invertv" not in Terrain.modifiers:
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
            Terrain.modifiers[len(Terrain.modifiers)-1].name = "CAM-CUT: Invertv"
            Terrain.modifiers["CAM-CUT: Invertv"].mix_mode = 'DIF'
            Terrain.modifiers["CAM-CUT: Invertv"].mix_set = 'A'
            Terrain.modifiers["CAM-CUT: Invertv"].default_weight_b = 1
            Terrain.modifiers["CAM-CUT: Invertv"].vertex_group_a = Vcam
            Terrain.modifiers["CAM-CUT: Invertv"].show_expanded = False
            int+=1

        for p in Terrain.particle_systems:
            if "SCATTER" in p.name:
                Vcam_mix = "CAM-CUT: " + p.name[9:]
                if Vcam_mix not in Terrain.modifiers:
                    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                    Terrain.modifiers[len(Terrain.modifiers)-1].name = Vcam_mix
                    Terrain.modifiers[Vcam_mix].vertex_group_a = p.name
                    Terrain.modifiers[Vcam_mix].mask_vertex_group = p.name
                    Terrain.modifiers[Vcam_mix].vertex_group_b = Vcam
                    Terrain.modifiers[Vcam_mix].mix_mode = 'SUB'
                    Terrain.modifiers[Vcam_mix].mix_set = 'B'
                    Terrain.modifiers[Vcam_mix].show_expanded = False
                    if int==0:
                        part = [m for m in Terrain.modifiers if (m.type == 'PARTICLE_SYSTEM' or m.name[:7]=='CAM-DEN')]
                        for a in range(len(part)):
                            bpy.ops.object.modifier_move_up(modifier=Vcam_mix)


        #Cam Density Part ###################################
        C.view_layer.objects.active = CAM
        FOV = C.object.data.angle
        Dcam = "CAM-DEN: Camera-Dens"

        if Dcam not in C.scene.objects: ##### CREATION IF NOT HERE
            bpy.ops.mesh.primitive_cube_add(size=0.2)
            DIST = C.object
            DIST.rotation_euler = CAM.rotation_euler
            DIST.location       = CAM.location
            DIST.name = DIST.data.name = Dcam
            DIST.display_type = 'WIRE'
            DIST.hide_render  = True
            cy=DIST.cycles_visibility ;cy.camera=cy.transmission=cy.diffuse=cy.scatter=cy.glossy=cy.shadow= False

            ob_old_coll = DIST.users_collection 
            for o in ob_old_coll : ob_old_coll = o
            new_coll = CAM.users_collection 
            for o in new_coll : new_coll = o
            ob_old_coll.objects.unlink(DIST) ; new_coll.objects.link(DIST)
        else:                         ##### MOVE IF ALREADY HERE
            DIST = bpy.data.objects[Dcam]
            for ob in C.selected_objects: ob.select_set(state=False)
            DIST.select_set(state=True)
            C.view_layer.objects.active = DIST
            #DIST.hide_select = False
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            #for i in range(3): DIST.lock_rotation[i] = DIST.lock_location[i] = DIST.lock_scale[i] = False
            DIST.rotation_euler , DIST.location = CAM.rotation_euler , CAM.location
            #for i in range(3): DIST.lock_rotation[i] = DIST.lock_location[i] = DIST.lock_scale[i] = True

        for ob in C.selected_objects: ob.select_set(state=False) #make if else statement same 
        C.view_layer.objects.active = DIST #clear parent on DIST
        DIST.select_set(state=True) ; bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        C.view_layer.objects.active = CAM #create parenting from dist to cam
        CAM.select_set(state=True) ; bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        C.view_layer.objects.active = Terrain #terain only = selected and active
        Terrain.select_set(state=True) ; CAM.select_set(state=False) ; DIST.select_set(state=False)

        if Dcam not in Terrain.vertex_groups:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT') #'DESELECT'
            bpy.ops.object.vertex_group_add()
            bpy.context.object.vertex_groups[len(Terrain.vertex_groups)-1].name = Dcam
            bpy.context.scene.tool_settings.vertex_group_weight = 1
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()

        if Dcam not in Terrain.modifiers:
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_PROXIMITY')
            Terrain.modifiers[len(Terrain.modifiers)-1].name = Dcam
            Terrain.modifiers[Dcam].min_dist = 20
            Terrain.modifiers[Dcam].max_dist = 0
            Terrain.modifiers[Dcam].proximity_mode = 'GEOMETRY'
            Terrain.modifiers[Dcam].falloff_type = 'SHARP'
            Terrain.modifiers[Dcam].mask_constant = 0.9949
            Terrain.modifiers[Dcam].vertex_group = Dcam
            Terrain.modifiers[Dcam].target = DIST
            Terrain.modifiers[Dcam].show_expanded = False
            int+=1

        if "CAM-DEN: Invertv" not in Terrain.modifiers:
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
            Terrain.modifiers[len(Terrain.modifiers)-1].name = "CAM-DEN: Invertv"
            Terrain.modifiers["CAM-DEN: Invertv"].mix_mode   = 'DIF'
            Terrain.modifiers["CAM-DEN: Invertv"].mix_set    = 'A'
            Terrain.modifiers["CAM-DEN: Invertv"].default_weight_b = 1
            Terrain.modifiers["CAM-DEN: Invertv"].vertex_group_a   = Dcam
            Terrain.modifiers["CAM-DEN: Invertv"].show_expanded    = False
            int+=1

        for p in Terrain.particle_systems:
            if "SCATTER" in p.name:
                Dcam_mix = "CAM-DEN: " + p.name[9:]
                if Dcam_mix not in Terrain.modifiers:
                    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                    Terrain.modifiers[len(Terrain.modifiers)-1].name = Dcam_mix
                    Terrain.modifiers[Dcam_mix].vertex_group_a       = p.name
                    Terrain.modifiers[Dcam_mix].mask_vertex_group    = p.name
                    Terrain.modifiers[Dcam_mix].vertex_group_b = Dcam
                    Terrain.modifiers[Dcam_mix].mix_mode       = 'SUB'
                    Terrain.modifiers[Dcam_mix].mix_set        = 'B'
                    Terrain.modifiers[Dcam_mix].show_expanded  = False
                    if int==0:
                        part = [m for m in Terrain.modifiers if m.type == 'PARTICLE_SYSTEM']
                        for a in range(len(part)):
                            bpy.ops.object.modifier_move_up(modifier=Dcam_mix)




        #Set all in order ###################################
        if int!=0:
            list_of_part_modif = []
            for m in Terrain.modifiers:
                if m.type == 'PARTICLE_SYSTEM':
                    list_of_part_modif.append(m.name)
            for name in list_of_part_modif:
                while Terrain.modifiers[-1].name != name:
                    #print("move down")
                    bpy.ops.object.modifier_move_down(modifier=name)

        #remove viewport because better performance ###################################
        for name in partviewporttrue:
            Terrain.modifiers[name].show_viewport = True

        #update terrain ###################################
        bpy.ops.object.editmode_toggle() ; bpy.ops.object.editmode_toggle()
        return {'FINISHED'} 

class SCATTER_OT_delete_cam(bpy.types.Operator):
    bl_idname = "scatter.delete_cam"
    bl_label = "refresh/update particle system"
    bl_description = ""

    def execute(self, context):
        C = bpy.context
        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        for m in Terrain.modifiers:
           if (m.name[:7] == "CAM-DEN" or m.name[:7] == "CAM-CUT"):
               bpy.ops.object.modifier_remove(modifier=m.name)
        for o in C.scene.objects:
           if (o.name[:7] == "CAM-DEN" or o.name[:7] == "CAM-CUT"):
               bpy.data.objects.remove(o, do_unlink=True)
        terrain_coll_name = "SCATTER: ["+Terrain.name+"]"+" Particles"
        for coll_child in bpy.data.collections[terrain_coll_name].children:
            if coll_child.name == "CAM-CUT: Camera-Clip":
                bpy.data.collections.remove(bpy.data.collections[coll_child.name])
        return {'FINISHED'} 


class SCATTER_OT_toggle_clip(bpy.types.Operator):
    bl_idname = "scatter.toggle_clip"
    bl_label = ""
    bl_description = ""

    psys : bpy.props.StringProperty()
    def execute(self, context):
        psys=self.psys

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        for m in Terrain.modifiers:
            if m.name[:7] == "CAM-CUT":
                if psys[9:] in m.name:
                    if m.show_viewport == 1: m.show_render = 0 ; m.show_viewport = 0
                    elif m.show_viewport == 0: m.show_render = 1 ; m.show_viewport = 1
        return {'FINISHED'}

class SCATTER_OT_toggle_dens(bpy.types.Operator):
    bl_idname = "scatter.toggle_dens"
    bl_label = ""
    bl_description = ""

    psys : bpy.props.StringProperty()
    def execute(self, context):
        psys=self.psys

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        for m in Terrain.modifiers:
            if m.name[:7] == "CAM-DEN":
                if psys[9:] in m.name:
                    if m.show_viewport == 1: m.show_render = 0 ; m.show_viewport = 0
                    elif m.show_viewport == 0: m.show_render = 1 ; m.show_viewport = 1
        return {'FINISHED'} 

######################################################################################


class SCATTER_OT_auto_toggle(bpy.types.Operator):
    bl_idname = "scatter.auto_toggle"
    bl_label = ""
    bl_description = ""

    def execute(self, context):

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        if "refresh_watch" not in Terrain:
            Terrain["refresh_watch"]=False

        was_not = False
        if Terrain not in bpy.context.selected_objects: Terrain.select_set(state=True) ; was_not = True
        override = bpy.context.copy()
        if was_not == True: Terrain.select_set(state=False)

        cam = bpy.data.objects["CAM-CUT: Camera-Clip"] ; boo = bpy.context.scene.camera
        cam_loc_xyz = cam.location[0]       + cam.location[1]       + cam.location[2]       + boo.location[0]       + boo.location[1]       + boo.location[2] 
        cam_siz_xyz = cam.scale[0]          + cam.scale[1]          + cam.scale[2]          + boo.scale[0]          + boo.scale[1]          + boo.scale[2] 
        cam_rot_xyz = cam.rotation_euler[0] + cam.rotation_euler[1] + cam.rotation_euler[2] + boo.rotation_euler[0] + boo.rotation_euler[1] + boo.rotation_euler[2]
        tot  = cam_loc_xyz + cam_siz_xyz + cam_rot_xyz

        if Terrain["refresh_watch"]==False:
            Terrain["refresh_watch"]=True
            bpy.context.scene["scene_cam_location"] = tot
            #print("timer started")
            bpy.app.timers.register(functools.partial(check_terrain_refresh, override), first_interval=1)
        else: Terrain["refresh_watch"]=False
        return {'FINISHED'} 


def check_terrain_refresh(override): #TIMER
    C_Slots = bpy.context.scene.C_Slots_settings
    Terrain = C_Slots.Terrain_pointer
    if Terrain["refresh_watch"] == False:
        print("timer aborted")
        return None
    #print("check")

    cam = bpy.data.objects["CAM-CUT: Camera-Clip"] ; boo = bpy.context.scene.camera
    cam_loc_xyz = cam.location[0]       + cam.location[1]       + cam.location[2]       + boo.location[0]       + boo.location[1]       + boo.location[2] 
    cam_siz_xyz = cam.scale[0]          + cam.scale[1]          + cam.scale[2]          + boo.scale[0]          + boo.scale[1]          + boo.scale[2] 
    cam_rot_xyz = cam.rotation_euler[0] + cam.rotation_euler[1] + cam.rotation_euler[2] + boo.rotation_euler[0] + boo.rotation_euler[1] + boo.rotation_euler[2]
    tot  = cam_loc_xyz + cam_siz_xyz + cam_rot_xyz

    if bpy.context.scene["scene_cam_location"] != tot:
        bpy.context.scene["scene_cam_location"] = tot
        bpy.ops.transform.translate(override,value=(0,0,0)) #update particles
    return 1




######################################################################################
#   .oooooo.   ooooooooo.        ooooooooooooo                     oooo
#  d8P'  `Y8b  `888   `Y88.      8'   888   `8                     `888
# 888      888  888   .d88'           888       .ooooo.   .ooooo.   888   .oooo.o
# 888      888  888ooo88P'            888      d88' `88b d88' `88b  888  d88(  "8
# 888      888  888                   888      888   888 888   888  888  `"Y88b.
# `88b    d88'  888                   888      888   888 888   888  888  o.  )88b
#  `Y8bood8P'  o888o                 o888o     `Y8bod8P' `Y8bod8P' o888o 8""888P'
#  
######################################################################################

class SCATTER_OT_refresh(bpy.types.Operator):
    bl_idname = "scatter.refresh"
    bl_label = "refresh/update particle system"
    bl_description = ""
    def execute(self, context):

        C_Slots = bpy.context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        A = bpy.context.object
        S = bpy.context.selected_objects
        for o in S: o.select_set(state=False)
        bpy.context.view_layer.objects.active = Terrain
        Terrain.select_set(state=True)

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()

        Terrain.select_set(state=False)
        bpy.context.view_layer.objects.active = A
        for o in S: o.select_set(state=True)

        return {'FINISHED'} 

class SCATTER_OT_quick_turn(bpy.types.Operator):
    bl_idname = "scatter.quick_turn"
    bl_label = "Quick turn particles correction tool"
    bl_description = ""
    def execute(self, context):
        next = False
        for ob in bpy.context.selected_objects:
            if ob.rotation_euler.x == 0:
                if "SCATTER: ["+ob.name+"] Particles" not in bpy.context.scene.collection.children:
                    ob.rotation_euler.x = -1.5708
                    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                    next = True
        if next == True: 
            for ob in bpy.context.selected_objects:
                ob.rotation_euler.x = 1.5708
        return {'FINISHED'} 

class SCATTER_OT_low_origin(bpy.types.Operator):
    bl_idname = "scatter.low_origin"
    bl_label = "Quickly set the origin to the lowest point from the particle on the global Z axis"
    bl_description = ""
    def execute(self, context):

        Selection = bpy.context.selected_objects
        A = bpy.context.view_layer.objects.active

        for ob in bpy.context.selected_objects:
            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

            o  = ob                  # active object
            mw = o.matrix_world      # Active object's world matrix
            cursor_loc = 0

            glob_vertex_coordinates = [ mw @ v.co for v in o.data.vertices ] # Global coordinates of vertices
            minZ = min( [ co.z for co in glob_vertex_coordinates ] )         # Find the lowest Z value amongst the object's verts
            mat = o.matrix_world                                             # World martix

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.editmode_toggle()

            for v in o.data.vertices: # Select all the vertices that are on the lowest Z
                if (mw @ v.co).z == minZ: cursor_loc = mat@v.co #wm@v.col = global data
            bpy.context.scene.cursor.location = cursor_loc
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        for ob in Selection: ob.select_set(state=True)
        bpy.context.view_layer.objects.active = A

        return {'FINISHED'} 

class SCATTER_OT_is_proxy_of_active(bpy.types.Operator):
    bl_idname = "scatter.is_proxy_of_active"
    bl_label = "Quickly set up a correct proxy name"
    bl_description = ""
    def execute(self, context):
        if len(bpy.context.selected_objects) !=2:
            ShowMessageBox("Two object in selection needed", "Be Careful" ,"ERROR")
            return {'FINISHED'} 
        A = bpy.context.object
        for s in bpy.context.selected_objects:
            if s is not A: B = s
        B.name = A.name + " [proxy]"
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.context.view_layer.objects.active = B
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.context.view_layer.objects.active = A
        B.location[2] = A.location[2]
        B.rotation_euler = A.rotation_euler
        return {'FINISHED'} 
        

class SCATTER_OT_particle_optimizer(bpy.types.Operator):
    bl_idname = "scatter.particle_optimizer"
    bl_label = "Particles Optimizer"
    bl_description = "optimize the particle on viewport by removing n% of verticles"
    def execute(self, context):

        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        Selection = bpy.context.selected_objects
        Active = bpy.context.view_layer.objects.active

        for ob in bpy.context.selected_objects:

            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob

            A = ob
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_random(percent= addon_prefs.particle_optimizer, seed=0, action='SELECT') #1-50%
            if "Particle optimisation" in A.vertex_groups:
                bpy.context.object.vertex_groups.remove(A.vertex_groups[A.vertex_groups['Particle optimisation'].index])
            bpy.ops.object.vertex_group_add()
            A.vertex_groups[len(A.vertex_groups)-1].name = 'Particle optimisation'
            bpy.context.scene.tool_settings.vertex_group_weight = 1
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.editmode_toggle()
            if "Particle optimisation" not in A.modifiers:
                bpy.ops.object.modifier_add(type='MASK')
                A.modifiers[len(A.modifiers)-1].name = 'Particle optimisation'
                A.modifiers[len(A.modifiers)-1].vertex_group = 'Particle optimisation'
                A.modifiers[len(A.modifiers)-1].invert_vertex_group = True
                A.modifiers[len(A.modifiers)-1].show_render = False

        for ob in Selection: ob.select_set(state=True)
        bpy.context.view_layer.objects.active = Active

        return {'FINISHED'}

class SCATTER_OT_particle_optimizer_remover(bpy.types.Operator):
    bl_idname = "scatter.particle_optimizer_remover"
    bl_label = "Particles Optimizer Remove"
    bl_description = ""
    def execute(self, context):

        Selection = bpy.context.selected_objects
        Active = bpy.context.view_layer.objects.active

        for ob in bpy.context.selected_objects:

            bpy.ops.object.select_all(action='DESELECT')
            ob.select_set(state=True)
            bpy.context.view_layer.objects.active = ob
            ob = bpy.context.object
            if 'Particle optimisation' in ob.modifiers: bpy.ops.object.modifier_remove(modifier="Particle optimisation")

        for ob in Selection: ob.select_set(state=True)
        bpy.context.view_layer.objects.active = Active
        return {'FINISHED'}


class SCATTER_OT_disp_small(bpy.types.Operator):
    bl_idname = "scatter.disp_small"
    bl_label = "Quick give noise to terrain"
    bl_description = ""
    def execute(self, context):
        A = bpy.context.object
        name="SCATTER: Noise Displace (Small)"

        if len(A.data.polygons) < 100:
            ShowMessageBox("Your terrain don't have enough geometry to be displaced", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        if name not in A.modifiers:
            bpy.ops.object.modifier_add(type='DISPLACE')
            A.modifiers[len(A.modifiers)-1].name = name
            A.modifiers[name].texture_coords = 'GLOBAL'
            A.modifiers[name].show_expanded = False
            A.modifiers[name].mid_level = 0
            modifier_always_on_top(name)

            if name not in bpy.data.textures:
                bpy.ops.texture.new()
                bpy.data.textures[len(bpy.data.textures)-1].name = name
                bpy.data.textures[name].type = 'MUSGRAVE'
                bpy.data.textures[name].noise_scale = 1.25
                bpy.data.textures[name].noise_intensity = 0.045
                A.modifiers[name].texture = bpy.data.textures[len(bpy.data.textures)-1]
            else:
                A.modifiers[name].texture = bpy.data.textures[name]
        else:
            modifier_always_on_top(name)
        return {'FINISHED'} 

class SCATTER_OT_disp_big(bpy.types.Operator):
    bl_idname = "scatter.disp_big"
    bl_label = "Quick give noise to terrain"
    bl_description = ""
    def execute(self, context):
        A = bpy.context.object
        name="SCATTER: Noise Displace (Big)"

        if len(A.data.polygons) < 100:
            ShowMessageBox("Your terrain don't have enough geometry to be displaced", "Be Careful" ,"ERROR")
            return {'FINISHED'}

        if name not in A.modifiers:
            bpy.ops.object.modifier_add(type='DISPLACE')
            A.modifiers[len(A.modifiers)-1].name = name
            A.modifiers[name].texture_coords = 'GLOBAL'
            A.modifiers[name].show_expanded = False
            A.modifiers[name].mid_level = 0
            modifier_always_on_top(name)

            if name not in bpy.data.textures:
                bpy.ops.texture.new()
                bpy.data.textures[len(bpy.data.textures)-1].name = name
                bpy.data.textures[name].type = 'MUSGRAVE'
                bpy.data.textures[name].noise_scale = 15
                bpy.data.textures[name].noise_intensity = 0.125
                A.modifiers[name].texture = bpy.data.textures[len(bpy.data.textures)-1]
            else: A.modifiers[name].texture = bpy.data.textures[name]
        else: modifier_always_on_top(name)
        return {'FINISHED'} 

class SCATTER_OT_remove_apply(bpy.types.Operator):
    bl_idname = "scatter.remove_apply"
    bl_label = "remove or apply"
    bl_description = ""
    is_apply : bpy.props.BoolProperty()
    def execute(self, context):
        is_apply=self.is_apply
        A = bpy.context.object

        for m in A.modifiers:
            if "Noise" in m.name:
                if is_apply == True:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=m.name)
                else: bpy.ops.object.modifier_remove(modifier=m.name)
        return {'FINISHED'}


class SCATTER_OT_import_thumbnail_scene(bpy.types.Operator):
    bl_idname = "scatter.import_thumbnail_scene"
    bl_label = ""
    bl_description = "(create your own preview with the same scene as used"

    def execute(self, context):

        scenes =[sc.name for sc in bpy.data.scenes]

        if "Scatter Thumbnail Scene" not in scenes:
            directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
            thumb_dir   = directory + "__thumbnail__"
            thumb_blend = directory + "__thumbnail__" + ".blend"
            os.rename(thumb_dir,thumb_blend)
            FILEPATH =  thumb_blend

            with bpy.data.libraries.load(FILEPATH) as (data_from, data_to):
                for attr in dir(data_to): setattr(data_to, attr, getattr(data_from, attr))

            os.rename(thumb_blend,thumb_dir)
            ShowMessageBox('"Scatter Thumbnail Scene" is now in your file scenes list (top right)', "Thumbnail Scenes added !",'QUESTION')
        else: ShowMessageBox('"Scatter Thumbnail Scene" is already in your file scenes list (top right)', "Thumbnail Scenes already in file !",'QUESTION')

        return {'FINISHED'}


class SCATTER_OT_import_proxies(bpy.types.Operator):
    bl_idname = "scatter.import_proxies"
    bl_label = ""
    bl_description = "add some basic proxies mesh in your scene"

    def execute(self, context):

        directory  = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
        prev_dir   = directory + "__proxies__"
        prev_blend = directory + "__proxies__" + ".blend"

        os.rename(prev_dir,prev_blend)

        FILEPATH  =  prev_blend
        section   =  '\\Object\\'
        dirr      =  FILEPATH + section
        objects   = [ "__proxy.text__"]
        for i in range(17): #(000-016)
            objects.append("__proxy."+str(f"{i:03d}")+"__")
        print(objects)

        obj_scene  = [sc.name for sc in bpy.context.scene.objects]

        for obj in objects:
            if obj not in obj_scene: bpy.ops.wm.append(filename=obj,directory=dirr)
            else: print("prox already in scene")

        os.rename(prev_blend,prev_dir)
        return {'FINISHED'}

######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne
######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne
######################################################################################
######################################################################################
######################################################################################
##########################################################################Big Money-ne
#
#ooooooooo.                         o8o               .
#`888   `Y88.                       `"'             .o8
# 888   .d88'  .ooooo.   .oooooooo oooo   .oooo.o .o888oo  .ooooo.  oooo d8b
# 888ooo88P'  d88' `88b 888' `88b  `888  d88(  "8   888   d88' `88b `888""8P
# 888`88b.    888ooo888 888   888   888  `"Y88b.    888   888ooo888  888
# 888  `88b.  888    .o `88bod8P'   888  o.  )88b   888 . 888    .o  888
#o888o  o888o `Y8bod8P' `8oooooo.  o888o 8""888P'   "888" `Y8bod8P' d888b
#                       d"     YD
#                       "Y88888P'
######################################################################################


addon_keymaps = [] 
         
def get_addon_preferences():
    #quick wrapper for referencing addon preferences
    addon_preferences = bpy.context.user_preferences.addons[__name__].preferences
    return addon_preferences

def get_hotkey_entry_item(km, kmi_name):
    #returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
    #if there are multiple hotkeys!)
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            return km_item
    return None 

def add_hotkey():
    addon_preferences = context.preferences.addons[__name__].preferences
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')   #shortcut for all spaces if you want to change the space, its this line 
    kmi = km.keymap_items.new(SCATTER_OT_C_Slots.bl_idname, 'P', 'PRESS', ctrl=True, shift=True, alt=False)
    #kmi.active = True
    addon_keymaps.append(kmi)

def remove_hotkey():
    #clears all addon level keymap hotkeys stored in addon_keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps['Window']  #shortcut for all spaces if you want to change the space, its this line 
    for kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        #wm.keyconfigs.addon.keymaps.remove(kmi)  #this code will remove EVERY user keymap in pref !! bad bad bad so right now kemap will stay 
    addon_keymaps.clear()

######################################################################################

classes = {
    SCATTER_AddonPref,
    SCATTER_PT_Tools,
    SCATTER_PT_slider,
    SCATTER_PT_Scatter_OP,
    SCATTER_OT_C_Slots,
    SCATTER_OT_C_Slots_PresetsAdd,
    Scatter_MT_C_Slots_PresetMenu,
    SCATTER_OT_C_Slots_Settings,
    SCATTER_OT_C_Slots_Settings_reset,
    SCATTER_OT_Open_Directory,
    SCATTER_OT_C_Slots_Quick_addpreset,
    SCATTER_OT_C_Slots_del_confirm,
    SCATTER_PIE_confirm_overwrite,
    SCATTER_OT_C_Slots_overwrite,
    SCATTER_OT_Bool_Path,
    SCATTER_OT_quick_turn,    
    SCATTER_OT_refresh,
    SCATTER_OT_disp_small,
    SCATTER_OT_disp_big,
    SCATTER_OT_particle_optimizer,
    SCATTER_OT_toggle_proxy,
    SCATTER_OT_set_up_proxy,
    SCATTER_OT_activeisname,
    SCATTER_OT_destroycurve,
    SCATTER_OT_removecurve,
    SCATTER_OT_inverseinfluence,
    SCATTER_OT_curvesliderinfluence,
    SCATTER_OT_slider_is_bounds,
    SCATTER_OT_collremove,
    SCATTER_OT_colladd,
    SCATTER_OT_slider_boolean,
    SCATTER_OT_slider_persquaremeters,
    SCATTER_OT_slider_remov_system,
    SCATTER_OT_slider_create_tex,
    SCATTER_OT_slider_batch_dis,
    SCATTER_OT_slider_batch_emi,
    SCATTER_OT_slider_batch_emisquare,
    SCATTER_OT_slider_batch_seed,
    SCATTER_OT_slider_batch_seed_random,
    SCATTER_OT_slider_batch_r_scale,
    SCATTER_OT_slider_batch_r_rot,
    SCATTER_OT_slider_batch_r_rot_tot,
    SCATTER_OT_slider_batch_t_idens,
    SCATTER_OT_slider_batch_t_iscal,
    SCATTER_OT_slider_batch_t_scal,
    SCATTER_OT_slider_batch_t_scal_ran,
    SCATTER_OT_slider_batch_t_off,
    SCATTER_OT_slider_batch_t_off_ran,
    SCATTER_OT_slider_batch_t_brigh,
    SCATTER_OT_slider_batch_t_brigh_ran,
    SCATTER_OT_slider_batch_t_contr,
    SCATTER_OT_slider_batch_t_contr_ran,
    SCATTER_OT_parameter,
    SCATTER_OT_listen_to_view,
    SCATTER_OT_toggle_proxy_all,
    SCATTER_OT_is_proxy_of_active,
    SCATTER_OT_low_origin,
    SCATTER_OT_remove_apply,
    SCATTER_OT_particle_optimizer_remover,
    SCATTER_OT_camera_crop_and_density,
    SCATTER_OT_delete_cam,
    SCATTER_OT_toggle_clip,
    SCATTER_OT_toggle_dens,
    SCATTER_OT_how_much,
    SCATTER_OT_how_much2,
    SCATTER_OT_selection_to_coll,
    SCATTER_OT_auto_toggle,
    SCATTER_OT_paint,
    SCATTER_OT_hidecurve,
    SCATTER_OT_paint_del,
    SCATTER_OT_paint_infl_rem,
    SCATTER_OT_paint_show,
    SCATTER_OT_paint_part_infl,
    SCATTER_OT_paint_go_in_weight,
    SCATTER_OT_paint_invert,
    SCATTER_OT_bool_add_inlfe,
    SCATTER_OT_bool_open_min_tab,
    SCATTER_OT_paint_clear,
    SCATTER_OT_refresh_preview_img,
    SCATTER_OT_skip_prev,
    SCATTER_OT_active_to_target,
    SCATTER_OT_add_remove,
    SCATTER_OT_terrain_is_active,
    SCATTER_OT_import_thumbnail_scene,
    SCATTER_OT_import_proxies,
    SCATTER_OT_slider_img_enum_choose,
    SCATTER_OT_slider_img_create_invert,
    SCATTER_OT_slider_img_open_direct,
    SCATTER_OT_img_skip_prev,
    SCATTER_OT_particles_orientation,
    }
    

preview_collections = {} #img preview

######################################################################################

def update_and_exec_preset_from_enum(self, context):
    print("enum preview change detected")
    enum_name   = bpy.data.window_managers["WinMan"].my_previews
    directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
    C_Slots     = bpy.context.scene.C_Slots_settings
    bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label = enum_name[:-4].title()
    bpy.ops.script.python_file_run(filepath=directory+enum_name[:-4]+".py")

# def update_and_exec_preset_from_enum(self, context):
#     print("enum preview change detected")
#     enum_name   = bpy.data.window_managers["WinMan"].my_previews
#     directory   = os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\")
#     C_Slots     = bpy.context.scene.C_Slots_settings
#     bpy.types.Scatter_MT_C_Slots_PresetMenu.bl_label = enum_name[:-4].title()
#     bpy.ops.script.python_file_run(filepath=directory+enum_name[:-4]+".py")


def register():
    import bpy, os

    #img preview
    bpy.types.WindowManager.my_previews_dir = bpy.props.StringProperty(name="Folder Path",subtype='DIR_PATH',default=os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\"))   #r'C:\Users\doria\AppData\Roaming\Blender Foundation\Blender\2.80\scripts\presets\scatter_presets_custom')
    bpy.types.WindowManager.my_previews     = bpy.props.EnumProperty(items=enum_previews_from_directory_items, update=update_and_exec_preset_from_enum)
    #text preview
    bpy.types.WindowManager.my_textures_dir = bpy.props.StringProperty(name="Folder Path",subtype='DIR_PATH',default=os.path.join(bpy.utils.user_resource('SCRIPTS'), "presets", "scatter_presets_custom\\__textures__\\"))   #r'C:\Users\doria\AppData\Roaming\Blender Foundation\Blender\2.80\scripts\presets\scatter_presets_custom')
    bpy.types.WindowManager.my_textures     = bpy.props.EnumProperty(items=enum_previews_from_directory_text)#, update=update_and_exec_preset_from_enum)
    
    #img preview
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()
    preview_collections["main"] = pcoll

    #text preview
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_textures_dir = ""
    pcoll.my_textures = ()
    preview_collections["text"] = pcoll

    #reg
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.C_Slots_settings = bpy.props.PointerProperty(type=SCATTER_OT_C_Slots_Settings)
    bpy.app.handlers.render_pre.append(pre)   #RIGHT BEFORE RENDER
    bpy.app.handlers.render_post.append(post) #RIGHT AFTER RENDER
    scatter_presets_custom_folder_setup()
    #add_hotkey()


def unregister():
    import bpy

    #img preview
    del bpy.types.WindowManager.my_previews
    for pcoll in preview_collections.values(): bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    #unreg
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.C_Slots_settings
    #remove_hotkey()

if __name__ == "__main__":
    register()
