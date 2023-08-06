__version__ = "0.0a1.post3"

import augmentedtree.core
from augmentedtree.core import (
    MappingSchema,
    MappingSchemaBuilder,
    ALL_ITEMS,
    AUGMENTATION_FOR_MAPPING,
    AUGMENTATION_FOR_SEQUENCE,
    AUGMENTATION_FOR_VALUES,
    PRIMARYKEY_KEY,
    PRIMARYVALUE_KEY,
    LeafType,
    get_augmentation_classes,
    set_augmentation_classes,
    KeyLink,
    TreePath,
    use_augmentation_method_for_type,
    use_mappingtree_schema,
    use_mappingtree_schemas,
)
from augmentedtree.augmentation import (
    augment_datastructure,
    _augment,
    dumps_atree,
    print_atree,
)
from augmentedtree.abc import (
    AnAugmentedTreeItem,
    AnAugmentedCollection
)
from augmentedtree.treeitems import (
    ATreeItem,
    ACollectionTreeItem,
    ValueTreeItem,
    SequenceTreeItem,
    MappingTreeItem
)
from augmentedtree.tree import (
    AugmentedTree,
    AugmentedItemSelection,
    RegularExpressionPart,
    UnixFilePatternPart,
)


set_augmentation_classes("default", AUGMENTATION_FOR_MAPPING, MappingTreeItem)
set_augmentation_classes("default", AUGMENTATION_FOR_SEQUENCE, SequenceTreeItem)
set_augmentation_classes("default", AUGMENTATION_FOR_VALUES, ValueTreeItem)
