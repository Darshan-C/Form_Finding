from io import BytesIO
import json
from trimesh import load
from trimesh.exchange.gltf import export_glb

from viktor import ViktorController, File
from viktor.parametrization import ViktorParametrization
from viktor.parametrization import NumberField, Section, BooleanField
from viktor.parametrization import Text
from viktor.external.generic import GenericAnalysis
from viktor.views import GeometryAndDataView
from viktor.views import GeometryAndDataResult
from viktor.views import DataGroup
from viktor.views import DataItem


class Parametrization(ViktorParametrization):
    
    Introduction = Text('### This VIKTOR app is an integration with grasshopper. \nWith grasshopper it creates a '
                     'Form Finding Tool.')
    

    Square_Size = NumberField("Surface Size", suffix="m", default=5, variant= 'slider', min = 5, max = 10)
    Point_Region = NumberField("Point Region", variant= 'slider', suffix="m", default=2, min = 1, max = 4)
    Points_Count = NumberField("Point Count", variant= 'slider', suffix="m", default=2, min = 1, max = 4)
    Random_Pts_Seeds = NumberField("Building rotation", variant= 'slider', suffix="m", default=1, min = 1, max = 100)
    UV = NumberField("Division of mesh", variant= 'slider', suffix="m", default=20, min = 10, max = 30)
    Min_Pt_Ht = NumberField("Minimum Point Height", variant= 'slider', suffix="m", default=5, min = 1, max = 10)
    Max_Pt_Ht = NumberField("Maximum Point Height", variant= 'slider', suffix="m", default=12, min = 1, max = 15)
    Random_Points_Ht = NumberField("Random height of points", variant= 'slider', suffix="m", default=10, min = 0, max = 100)
    LengthFactor = NumberField("Length Factor", variant= 'slider', suffix="m", default=0.7, min = 0, max = 1.00)
    Button = BooleanField('False / True')

    


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @GeometryAndDataView("Geometry", duration_guess= 800, update_label='Run Grasshopper')
    def run_grasshopper(self, params, **kwargs):

        # Create a JSON file from the input parameters
        input_json = json.dumps(params)

        # Generate the input files
        files = [
            ('input.json', BytesIO(bytes(input_json, 'utf8'))),
        ]

        # Run the Grasshopper analysis and obtain the output files
        generic_analysis = GenericAnalysis(files=files, executable_key="run_grasshopper",
                                           output_filenames=["output_data.json", "geometry.obj"])
        generic_analysis.execute(timeout=60)
        output_file = generic_analysis.get_output_file("output_data.json")
        object_file = generic_analysis.get_output_file("geometry.obj")

        # Convert OBJ to GLB file
        trimesh_scene = load(object_file, file_type="obj")
        geometry = File()
        with geometry.open_binary() as writable_buffer:
            writable_buffer.write(export_glb(trimesh_scene))

        # Get volume from output data file
        output_dict = json.loads(output_file.getvalue())
        data = DataGroup(
            DataItem('Volume', output_dict['volume'])
        )
        return GeometryAndDataResult(geometry, data)
