import bpy
import os
import shutil

# === CONFIGURE PATHS HERE ===
input_folder = r"C:\User_input"
output_folder = r"C:\Users_output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

def import_fbx(filepath):
    bpy.ops.import_scene.fbx(filepath=filepath)

def export_obj(filepath):
    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=False,
        apply_modifiers=True,
        export_uv=True,
        export_normals=True,
        export_materials=True,
        path_mode='COPY'
    )

def copy_png_textures(obj, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for mat_slot in obj.material_slots:
        mat = mat_slot.material
        if mat and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    src_path = bpy.path.abspath(node.image.filepath)
                    if os.path.isfile(src_path):
                        shutil.copy(src_path, dest_folder)

def process_fbx(fbx_path, relative_path=""):
    clear_scene()
    import_fbx(fbx_path)

    # Unpack embedded Unreal textures
    bpy.ops.file.unpack_all(method='WRITE_LOCAL')

    if relative_path:
        obj_subfolder = os.path.join(output_folder, relative_path)
        os.makedirs(obj_subfolder, exist_ok=True)
    else:
        obj_subfolder = output_folder

    filename = os.path.splitext(os.path.basename(fbx_path))[0]
    obj_path = os.path.join(obj_subfolder, filename + ".obj")

    export_obj(obj_path)
    print(f"Exported: {obj_path}")

    # Copy textures used by meshes
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            copy_png_textures(obj, obj_subfolder)

def main():
    for root, dirs, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)

        for f in files:
            if f.lower().endswith(".fbx"):
                fbx_path = os.path.join(root, f)

                process_fbx(
                    fbx_path,
                    relative_path if relative_path != "." else ""
                )

if __name__ == "__main__":
    main()
