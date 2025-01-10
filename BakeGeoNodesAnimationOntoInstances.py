bl_info = {
    "name": "Bake Geo Nodes Animation Onto Instances",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (1, 4),
    "author": "Benjamin Round (with assistance from ChatGPT)",
    "description": "Bakes animated transforms from Geometry Nodes instances to keyframes with frame skipping.\nAccess addon from Object > Apply.",
}

import bpy


def bake_geo_nodes_animation(skip_frames=20):
    # Get the active object (the one with the Geometry Nodes modifier)
    active_obj = bpy.context.active_object

    if not active_obj or 'GeometryNodes' not in active_obj.modifiers:
        print("Please select an object with a Geometry Nodes modifier.")
        return

    # Get the frame range
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    # Ensure the object is in Object Mode
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Store initial objects to track new instances
    initial_objects = set(bpy.data.objects)

    # List to store the instances from the first frame
    base_instances = []

    # Process frames with the specified skip interval
    for frame in range(frame_start, frame_end + 1, skip_frames):
        bpy.context.scene.frame_set(frame)
        print(f"Processing frame {frame}")

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select the active object
        active_obj.select_set(True)
        bpy.context.view_layer.objects.active = active_obj

        # Make instances real
        bpy.ops.object.duplicates_make_real()

        # Get all newly created objects (instances)
        new_objs = [obj for obj in bpy.context.selected_objects if obj not in initial_objects]

        if frame == frame_start:
            # On the first frame, store these objects as the base instances
            base_instances = new_objs.copy()
            # Ensure keyframes are inserted for the first frame
            for base_instance in base_instances:
                base_instance.location = base_instance.matrix_world.translation
                base_instance.rotation_euler = base_instance.matrix_world.to_euler()
                base_instance.scale = base_instance.matrix_world.to_scale()
                base_instance.keyframe_insert(data_path="location", frame=frame)
                base_instance.keyframe_insert(data_path="rotation_euler", frame=frame)
                base_instance.keyframe_insert(data_path="scale", frame=frame)
        else:
            # For subsequent frames, transfer transforms to the base instances and insert keyframes
            for idx, obj in enumerate(new_objs):
                if idx < len(base_instances):
                    base_instance = base_instances[idx]
                    base_instance.location = obj.matrix_world.translation
                    base_instance.rotation_euler = obj.matrix_world.to_euler()
                    base_instance.scale = obj.matrix_world.to_scale()
                    base_instance.keyframe_insert(data_path="location", frame=frame)
                    base_instance.keyframe_insert(data_path="rotation_euler", frame=frame)
                    base_instance.keyframe_insert(data_path="scale", frame=frame)

            # Delete all newly created objects, but keep their names intact
            for obj in new_objs:
                bpy.data.objects.remove(obj, do_unlink=True)

    # Handle the last frame separately
    bpy.context.scene.frame_set(frame_end)
    print(f"Processing end frame {frame_end}")

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select the active object
    active_obj.select_set(True)
    bpy.context.view_layer.objects.active = active_obj

    # Make instances real
    bpy.ops.object.duplicates_make_real()

    # Get all newly created objects (instances)
    new_objs = [obj for obj in bpy.context.selected_objects if obj not in initial_objects]

    # Transfer transforms to the base instances and insert keyframes for the last frame
    for idx, obj in enumerate(new_objs):
        if idx < len(base_instances):
            base_instance = base_instances[idx]
            base_instance.location = obj.matrix_world.translation
            base_instance.rotation_euler = obj.matrix_world.to_euler()
            base_instance.scale = obj.matrix_world.to_scale()
            base_instance.keyframe_insert(data_path="location", frame=frame_end)
            base_instance.keyframe_insert(data_path="rotation_euler", frame=frame_end)
            base_instance.keyframe_insert(data_path="scale", frame=frame_end)

    # Delete all newly created objects for the last frame
    for obj in new_objs:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Remove the Geometry Nodes modifier from the final instances
    for base_instance in base_instances:
        for modifier in base_instance.modifiers:
            if modifier.type == 'NODES':
                base_instance.modifiers.remove(modifier)

    print("Transforms baked into keyframes with frame skipping, and end frame ensured.")


class OBJECT_OT_BakeGeoNodesAnimation(bpy.types.Operator):
    """Bake Geometry Nodes Animation"""
    bl_idname = "object.bake_geo_nodes_animation"
    bl_label = "Bake Geo Nodes Animation"
    bl_options = {'REGISTER', 'UNDO'}

    skip_frames: bpy.props.IntProperty(
        name="Skip Frames",
        description="Number of frames to skip between keyframes",
        default=20,
        min=1,
    )

    def execute(self, context):
        bake_geo_nodes_animation(skip_frames=self.skip_frames)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_BakeGeoNodesAnimation.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_BakeGeoNodesAnimation)
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_BakeGeoNodesAnimation)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)


if __name__ == "__main__":
    register()
