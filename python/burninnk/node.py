import nuke
from burnin.api import BurninClient
from burnin.entity.surreal import Thing
from burnin.entity.media import FfmpegCMD
from burnin.entity.filetype import FileType
from burnin.entity.version import Version, VersionStatus
from burnin.entity.node import Node
from burnin.entity.utils import parse_node_path
from burnin.entity.utils import TypeWrapper
from pathlib import Path

import os
root_id = os.getenv("BURNIN_ROOT_ID")
print(root_id)
from burnin.api import BurninClient

delimeter = "/"
if os.name == 'nt':
    delimeter = "\\"

c_node = nuke.selectedNode()
#c_node = nuke.thisNode()

def buildFilePath(include_file_name: bool = False, component_path: str = None):

    node = c_node
    root_path = os.getenv("BURNIN_ROOT_PATH")
    root_name = os.getenv("BURNIN_ROOT_NAME")

    if component_path is None:
        component_path = node.knob("component_path").value()

    component_path = parse_node_path(component_path)

    if component_path.startswith('/'):
        component_path = component_path[1:]
    
    if component_path.startswith('\\'):
        component_path = component_path[1:]
    
    
    version_number = node.knob("version").value()

    if include_file_name:
        file_type = node.knob("file_type").value()

        frame_expression = "" 
        # check if its time dependent
        if node.knob("timedependent").value() == 1:
            frame_expression = ".####"

        file_name = component_path.split("/")[-1] + "_" + version_number + frame_expression + file_type

    file_path = Path(root_path) / root_name / component_path / version_number
    if include_file_name:
        return file_path / file_name
    else:
        return file_path
    


def BurninWriteV1():
    thisNode = c_node
    write_node = thisNode.input(0)
    node_class = write_node.Class()

    if node_class != "Write":
        nuke.message("❌ Upstream node should be a Write Node")
        return None

    component_path = thisNode.knob("component_path").value()
    component_id = Thing.from_ids(root_id, component_path + "/v000")
    version_node = Node.new_version(component_id, FileType.Image)

    burnin_client = BurninClient(nuke._burnin_client)
    
    try:
        version_node: Node = burnin_client.create_or_update_component_version(version_node)
        version_node_id = version_node.get_node_id_str()
        version_number = version_node_id.split("/")[-1]
        thisNode.knob("version").setValue(version_number)

        limit_range = thisNode.knob("limit_to_range").value()
        write_node.knob("use_limit").setValue(limit_range)
        
        start = 0
        end = 0
        if limit_range:
            #start = thisNode.knob("start").value()
            start = thisNode.knob("start").value()
            write_node.knob("first").setValue(int(start))     
            
            end = thisNode.knob("end").value()
            write_node.knob("last").setValue(int(end))

        file_path = buildFilePath(include_file_name=False)
        print(file_path)
        

        # TODO: need to change this for unix
        file_path_split = str(file_path).split("\\")
        file_name = file_path_split[-2] + "_" + file_path_split[-1]
  
        
        if limit_range:
            file_name_from_path =  file_name + ".####.exr"
            thumbnail_frame_number = str(int(start)).zfill(4)
            thumbnail_file_name = file_name + "." + thumbnail_frame_number + ".exr"
            print("HEY", thumbnail_frame_number)
        else:
            file_name_from_path = file_name + ".exr"
            thumbnail_file_name = file_name_from_path
        
        file_path = str(file_path) + "\\" + file_name_from_path

        # for sending into thumbnail path
        image_file_path = file_path.replace("####", "%04d")
        print(image_file_path)
        
        
        output_file_path = image_file_path.replace( file_name + ".%04d.exr", "thumbnail.png")
        print(output_file_path)
    
        ffmpeg = FfmpegCMD(image_file_path, output_file_path)
        print(type(ffmpeg))

        file_path = file_path.replace("\\", "/")
        thisNode.knob("dir_path").setValue(file_path)
        print(file_path)

        ## set wirite node path
        write_node.knob("file").setValue(str(file_path))
        write_node.knob("file_type").setValue(3) # set exr


        wace = thisNode.knob("write_ACES_compliant_EXR").value()
        write_node.knob("write_ACES_compliant_EXR").setValue(wace)

        


        thisNode.knob("status").setValue(VersionStatus.Incomplete.value)
        file_type = ".exr"
        print("limit range", start, end)
        nuke.execute(write_node, int(start),int(end),1)


        version_type: Version = version_node.node_type.data 
        version_type.comment = thisNode.knob("Comment").value()
        version_type.software = "nuke"
        head_file_name = image_file_path.split("/")[0]
        version_type.head_file = file_name_from_path
        version_type.status = VersionStatus.Published


        file_type: FileType = version_type.file_type.data
        file_type.file_name = file_name_from_path
        file_type.file_format = ".exr"
        
        if limit_range:
            file_type.time_dependent = True
            file_type.frame_range = [start, end, 1]

        format = thisNode.format()
        width = format.width()
        height = format.height()
        file_type.resolution = [width, height]
        file_type.color_space = "ACES"


        version_type.file_type = TypeWrapper(file_type)
        version_node.node_type = TypeWrapper(version_type)
        version_node.created_at = None

        version_node = burnin_client.commit_component_version(version_node)
        version_node_type: Version = version_node.node_type.data
        print(version_node)
        print(version_node_type)
        
        print(ffmpeg)
        #burnin_client.generate_thumbnail_from_image(ffmpeg)

        # Using positional arguments (recommended)
        ffmpeg_cmd = FfmpegCMD(
            Path(image_file_path),
            Path(output_file_path)
        )

        burnin_client.generate_thumbnail_from_image(ffmpeg)

    except Exception as e:
        print(str(e))
    #print(component_id)

BurninWriteV1()