from io import BytesIO
import json
from trimesh import load
from trimesh.exchange.gltf import export_glb

from viktor import ViktorController, File
from viktor.parametrization import ViktorParametrization
from viktor.parametrization import NumberField, BooleanField
from viktor.parametrization import Text
from viktor.external.generic import GenericAnalysis
from viktor.views import GeometryAndDataView
from viktor.views import GeometryAndDataResult
from viktor.views import DataGroup
from viktor.views import DataItem


class Parametrization(ViktorParametrization):
    
    Head = Text('# Form Finding')
    Introduction = Text('A Form Finding experiment created by using the grasshopper kangaroo Plugin. The mesh/ fabric acts as a tensile structure, where the corners are anchored and few internal points are transformed in Z-direction to manipulate the fabric/mesh. Multiple forms can be created by changing the parameters of an app.')

    Square_Size = NumberField("Surface Size", suffix="m", default=5, variant= 'slider', min = 5, max = 10, description= "Size of the surface.")
    Point_Region = NumberField("Point Region", variant= 'slider', suffix="m", default=2, min = 1, max = 4, description= "Area bound to generate point inside it.")
    Points_Count = NumberField("Point Count", variant= 'slider', default=2, min = 1, max = 4, description= "No. of points to manipulate surface.")
    Random_Pts_Seeds = NumberField("Building rotation", variant= 'slider', default=1, min = 1, max = 100, description= "Selects different random points each time.")
    UV = NumberField("Division of mesh", variant= 'slider', default=20, min = 10, max = 30, description= "Division of meshes for detailing.")
    Min_Pt_Ht = NumberField("Minimum Point Height", variant= 'slider', suffix="m", default=5, min = 1, max = 10, description= "Min. point height to consider for random value.")
    Max_Pt_Ht = NumberField("Maximum Point Height", variant= 'slider', suffix="m", default=12, min = 1, max = 15, description= "Max. point height to consider for random value.")
    Random_Points_Ht = NumberField("Random height of points", variant= 'slider', default=10, min = 0, max = 100, description= "Selects different random heights each time.")
    LengthFactor = NumberField("Length Factor", variant= 'slider', suffix="m", default=0.7, min = 0.00, max = 1.00, description= "Flexibilty of the mesh(0-Loose, 1-Tight).")
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
