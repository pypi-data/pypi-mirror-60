from augmentedtree import (
    print_atree,
    AugmentedTree,
    MappingSchema,
    use_mappingtree_schemas
)


nested_data = {
    "dic": {
        "6cb830d6-32ce-40dc-9744-37601e9c5458": {
            "metatype": "imagesequence",
            "type": "video",
            "frequency": 50000,
            "starttime": -1.7078E-07,
            "framecount": 1201,
            "filename": "100-RTL-0640#1201_5.0E+04_-1.7078E-07.avi",
            "rois": {
                "class": "RoiCollection",
                "description": "Rect of interests for digital image correlation.",
                "items": [
                    {
                        "metatype": "rectofinterest",
                        "class": "ParallelROI",
                        "name": "complete-area",
                        "roipoints": [[10.0, 50.0], [90.0, 50.0], [30.0, 100.0]],
                        "center_points": [[50.0, 50.0], [50.0, 75.0], [50.0, 100.0]]
                    },
                    {
                        "metatype": "rectofinterest",
                        "class": "ParallelROI",
                        "name": "crack-position",
                        "roipoints": [[20.0, 50.0], [40.0, 50.0], [30.0, 100.0]],
                        "center_points": [[30.0, 50.0], [30.0, 75.0], [30.0, 100.0]]
                    }
                ],
            },
            "time-seeds": [[0.001231, 0.001629, 209, None, None]]
        },
    },
    "etc.": "..."
}

VIDEO_SCHEMA = {
    MappingSchema.IDENTIFIER: ("metatype", "imagesequence"),
    MappingSchema.PRIMARYKEY: "type",
    MappingSchema.PRIMARYNAME: "filename",
    MappingSchema.METAFIELDKEYS: ["metatype", "name", "type", "frequency", "starttime", "framecount", "filename"],
}

ROI_COLLECTION_SCHEMA = {
    MappingSchema.IDENTIFIER: ("class", "RoiCollection"),
    MappingSchema.PRIMARYNAME: "description",
    MappingSchema.OUTERVALUES: "items",
}

ROI_SCHEMA = {
    MappingSchema.IDENTIFIER: ("metatype", "rectofinterest"),
    MappingSchema.PRIMARYKEY: "class",
    MappingSchema.PRIMARYNAME: "name",
    MappingSchema.METAFIELDKEYS: ["metatype", "class", "name"],
}

use_mappingtree_schemas(VIDEO_SCHEMA)
use_mappingtree_schemas(ROI_COLLECTION_SCHEMA)
use_mappingtree_schemas(ROI_SCHEMA)

atree = AugmentedTree(nested_data)
selectino = atree.select("roipoints")
print(selectino)
print_atree(atree)
