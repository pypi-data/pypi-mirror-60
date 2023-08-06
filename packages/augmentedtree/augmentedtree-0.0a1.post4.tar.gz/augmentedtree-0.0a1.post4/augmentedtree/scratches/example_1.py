from collections import Callable
from typing import Dict, Union, List, Any

from augmentedtree import (
    MappingTreeItem,
    LeafType,
    get_augmentation_classes,
    print_atree,
    MappingSchema,
)


from augmentedtree import (
    ATreeItem,
    use_augmentation_method_for_type,
    augment_datastructure,
    TreePath,
)

from augmentedtree.core import _augment_by_schema

class ActionDictItem(MappingTreeItem):
    def __init__(
        self,
        primarykey=None,
        primaryname=None,
        primaryvalue=None,
        outervaluekey=None,
        metadatakeys=None,
        real_key=None,
        field_types: Dict[str, Callable] = None,
        meta_attributes=None,
    ):
        super().__init__(
            primarykey=primarykey,
            primaryname=primaryname,
            primaryvalue=primaryvalue,
            outervaluekey=outervaluekey,
            metadatakeys=metadatakeys,
            real_key=real_key,
            field_types=field_types,
            meta_attributes=meta_attributes,
        )
        self.leaf_type = LeafType.ACTION
        self._actionkeys = []
        self.actions = {}

    def insert_child_at(self, key, child: ATreeItem):
        if child.leaf_type == LeafType.ACTION:
            if child.preuuid not in self._outervalues:
                self._children[key] = child
                self._childrenskeys.append(key)
            self.actions[key] = child
        else:
            self._childrenskeys.append(key)
        child.parent = self

    def get_pathmap(
        self, parent_path: TreePath = None, section_root_path: TreePath = None
    ):
        """
        Retrives a pathmap.

        Args:
            parent_path:
                TreePath of the parent.

        Returns:
            List[Tuple[TreePath, ATreeItem]]
        """
        pathmap = []
        my_real_path = [self.real_key]
        my_augmented_path = [self.primekey]
        my_associations = self.get_meta_attributes()
        if parent_path is not None:
            my_treepath = parent_path.join(
                real_path_parts_or_treepath=my_real_path,
                augmented_path_parts=my_augmented_path,
                meta_attributes=my_associations,
            )
        else:
            my_treepath = TreePath(my_real_path, my_augmented_path, my_associations)
        if self.parent is not None:
            pathmap.append((my_treepath, self.parent))

        for action_uuid, action in self._children.items():
            childs_pathmap = action.get_pathmap(
                my_treepath, section_root_path=my_treepath
            )
            pathmap.extend(childs_pathmap)
        return pathmap


class ActionTreeItem(MappingTreeItem):
    """
    Dieses `TreeItem` hat die Ziele:

    - verschachtelte `dict` (Mapping) zu enthalten, welche Listen enthalten
      (Sequences) können, welche ebenfalls `dict` als Elemente haben können.
    - zusätzliche Einträge/Information zu den einzelnen Werten ermöglichen.
    """

    def __init__(
        self,
        primarykey=None,
        primaryname=None,
        primaryvalue=None,
        outervaluekey=None,
        metadatakeys=None,
        real_key=None,
        field_types: Dict[str, Callable] = None,
        meta_attributes=None,
        table_root_item=None,
    ):
        super().__init__(
            primarykey=primarykey,
            primaryname=primaryname,
            primaryvalue=primaryvalue,
            outervaluekey=outervaluekey,
            metadatakeys=metadatakeys,
            real_key=real_key,
            field_types=field_types,
            meta_attributes=meta_attributes,
        )
        self.leaf_type = LeafType.ACTION
        self._actionkeys = []
        self.table_root_item = None
        assert (
            table_root_item is None
        ), "A table root item has to be defined for an action tree item."
        self.table_root_item = table_root_item

    def is_root(self):
        if self.parent is None:
            return True
        if self.parent.leaf_type != LeafType.ACTION:
            return True
        return False

    def get_pathmap(
        self, parent_path: TreePath = None, section_root_path: TreePath = None
    ):
        """
        Retrives a pathmap.

        Args:
            parent_path:
                TreePath of the parent.

        Returns:
            List[Tuple[TreePath, ATreeItem]]
        """
        pathmap = []
        my_real_path = [self.real_key]
        my_augmented_path = [self.primekey]
        my_associations = self.get_meta_attributes()
        if parent_path is not None:
            my_treepath = parent_path.join(
                real_path_parts_or_treepath=my_real_path,
                augmented_path_parts=my_augmented_path,
                meta_attributes=my_associations,
            )
            if section_root_path is not None:
                my_real_path = section_root_path.real_path_parts.copy()
                my_real_path.append(self.real_key)
            my_treepath.real_path_parts = my_real_path
        else:
            my_treepath = TreePath(my_real_path, my_augmented_path, my_associations)
        if self.parent is not None:
            pathmap.append((my_treepath, self))

        base_childs_path = TreePath(real_path=[self._outervaluekey])
        base_childs_path = my_treepath.join(base_childs_path)

        for childs_key, child in self._children.items():
            if child.leaf_type == LeafType.ACTION:
                childs_paths = child.get_pathmap(
                    parent_path=my_treepath, section_root_path=section_root_path
                )
            else:
                childs_paths = child.get_pathmap(parent_path=base_childs_path)
            pathmap.extend(childs_paths)
        return pathmap

    def mapping_children(self):
        for childkey in self._children:
            if childkey in self._actionkeys:
                continue
            yield self._children[childkey]

    def insert_child_at(self, key, child: ATreeItem):
        self._children[key] = child
        self._childrenskeys.append(key)
        if child.leaf_type == LeafType.ACTION:
            self._actionkeys.append(key)
        child.parent = self

    @property
    def preuuid(self):
        return self.primevalue["preuuid"]


def _augment_actiondict(
    parent: ATreeItem,
    childskey: Union[str, int],
    datastructure: Any,
    augmentclasses: dict,
) -> ATreeItem:
    action_root_item = _augment_by_schema(
        parent, childskey, datastructure, augmentclasses, do_recursion=False
    )
    actiondict = action_root_item.outervalues
    actions = {}
    for key, child in action_root_item.outervalues.items():
        if key[:2] == "__":
            continue
        action = _augment_by_schema(action_root_item, key, child, augmentclasses)
        actions[key] = action
        action.table_root_item = action_root_item

    for childs_uuid, action in actions.items():
        if action.preuuid in actions:
            previous_action_of_child = actions[action.preuuid]
            previous_action_of_child.insert_child_at(childs_uuid, action)
    return parent


if __name__ == "__main__":
    exampledata = {
        "904457d7-bcd1-4d2f-a8dc-a544474c2b7e": {
            MappingSchema.IDENTIFIER: "example-1",
            "name": "Pizza dough",
            "timestamp": "2020-01-09 20:46:02",
            "action": "make dough",
            "indigrients": {"Name": "FC4"},
            "__tree_schema_identifier": "pkde_action",
            },
            "3f7ee0d1-295b-4916-8e60-c5949162a892": {
                "uuid": "3f7ee0d1-295b-4916-8e60-c5949162a892",
                "preuuid": "904457d7-bcd1-4d2f-a8dc-a544474c2b7e",
                "project": "a89b5f88-b054-4177-b582-37aa20d0cb99",
                "name": "FC4",
                "timestamp": "2020-01-09 20:47:02",
                "action": "Fräsen",
                "value": {"Geometrie": "ISO 527-4 Typ 3", "Ausführer": "Ungefehr, S."},
                "__tree_schema_identifier": "pkde_action",
            },
            "0382b684-d777-4cd3-8fad-9a83739dcca5": {
                "uuid": "0382b684-d777-4cd3-8fad-9a83739dcca5",
                "preuuid": "3f7ee0d1-295b-4916-8e60-c5949162a892",
                "project": "a89b5f88-b054-4177-b582-37aa20d0cb99",
                "name": "FC4",
                "timestamp": "2020-01-09 20:48:02",
                "action": "Messen",
                "value": {"Breite#mm": 9.792514697152024},
                "__tree_schema_identifier": "pkde_action",
            },
        }
    }
    from exa5.models.treeitemjsonmodels import ACTIONTREEITEM, ACTIONDICT
    from augmentedtree import (
        register_mappingtree_jsonschema,
        set_augmentation_classes,
    )

    register_mappingtree_jsonschema(ACTIONTREEITEM)
    register_mappingtree_jsonschema(ACTIONDICT)
    set_augmentation_classes("default", "pkde_action", ActionTreeItem)
    set_augmentation_classes("default", "actiondict", ActionDictItem)
    use_augmentation_method_for_type("actiondict", _augment_actiondict)

    tree = augment_datastructure(actiontree)
    #print_tree(tree)
    #print_tree_items(tree)

    from augmentedtree import AugmentedTree

    print(actiontree["actiondict"]["0382b684-d777-4cd3-8fad-9a83739dcca5"]["value"]["Breite#mm"])


    pm = AugmentedTreeItemModel(tree)
    # print(pm)
    selection = pm.select("Breite")
    print(selection[-1])

    # print(selection[0])

    # df = pm._pathmap
    # for index, item in df.iterrows():
    #     print(item.augmented_path)
    # print(df["real_path"])
