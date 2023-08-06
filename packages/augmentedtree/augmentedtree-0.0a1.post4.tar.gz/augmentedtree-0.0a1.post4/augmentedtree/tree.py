from typing import Union, Mapping, Sequence, Dict, Any, Generator, List, Optional
from pandas import DataFrame
from augmentedtree.core import AUGMENTATION_ROOT_KEY, TreePath, NotSupportedError
from augmentedtree.abc import (
    AnAugmentedCollection,
    AnAugmentedTreeItem,
)
from augmentedtree.treeitems import TreeItems
from augmentedtree.augmentation import augment_datastructure, print_atree


UFP2RE_WILDCARD_QUESTIONMARK = "."
UFP2RE_WILDCARD_STAR = ".*?"
UFP2RE_FORWARDSLASH = "\/"


class UnixFilePatternPart(object):
    def __init__(self, *path_parts):
        self.path_parts = path_parts

    def to_re_pattern(self):
        re_path_parts = UnixFilePatternPart.convert_to_re_pattern(*self.path_parts)
        or_conditioned = "|".join(re_path_parts)
        return [or_conditioned]

    @staticmethod
    def convert_to_re_pattern(*unix_file_pattern):
        re_patterns = []
        for pattern in unix_file_pattern:
            result = pattern.replace("?", UFP2RE_WILDCARD_QUESTIONMARK)
            result = result.replace("*", UFP2RE_WILDCARD_STAR)
            result = result.replace("/", UFP2RE_FORWARDSLASH)
            re_patterns.append(result)
        return re_patterns

    def __str__(self):
        joined_parts = " -> ".join(self.path_parts)
        return "({})".format(joined_parts)


class RegularExpressionPart(object):
    def __init__(self, *path_parts):
        self.path_parts = path_parts

    def to_re_pattern(self):
        or_conditioned = "|".join(self.path_parts)
        return [or_conditioned]

    def __str__(self):
        joined_parts = " -> ".join(self.path_parts)
        return "({})".format(joined_parts)


class RegexPathQuery(object):
    REGEX_SEARCHING_PART_GROUP = "(\/{}).*"

    def __init__(self, path_parts):
        self.path_parts = path_parts
        self.search_pattern = RegexPathQuery.create_search_pattern(*path_parts)

    @staticmethod
    def create_search_pattern(*search_parts):
        parts_to_search = []
        ufpp = UnixFilePatternPart
        for search_part in search_parts:
            if isinstance(search_part, str):
                search_part_pattern = ufpp.convert_to_re_pattern(search_part)
            else:
                search_part_pattern = search_part.to_re_pattern()
            parts_to_search.extend(search_part_pattern)
        searchgroups = [
            RegexPathQuery.REGEX_SEARCHING_PART_GROUP.format(pathpart)
            for pathpart in parts_to_search
        ]
        search_pattern = ".*" + "".join(searchgroups)
        return search_pattern

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.search_pattern)


class Selectable(object):
    """
    This class enables and `AnAugmentedTreeItem` to be able to select
    items by parts of a path within the nested data.
    """

    def __call__(self, *path_parts: List[Union[str, int]]) -> List[AnAugmentedTreeItem]:
        """
        Makes a selection of tree items in regard of the given path
        parts. The path parts do not need to resemble the whole path.


        Args:
            path_parts: List[Union[str, int]]:
                Path parts for which tree items should be retrived.

        Returns:
            List[AnAugmentedTreeItem]:
                Tree items which fit to the given tree parts.
        """
        pass


class WhereRefineable(object):
    """
    This class enables and `AnAugmentedTreeItem` to be able to refine
    a selection with `where`.
    """

    def __call__(
        self, conditions: Dict[str, Any], **kwargs
    ) -> List[AnAugmentedTreeItem]:
        """
        Narrows a selection to tree items, which fits the given
        conditions.

        Args:
            conditions (Dict["str": Any]):


            **kwargs:

        Returns:

        """
        pass


# The whole section regarding selection of tree items has to be reworked.
# By this measure the 'Access to a protected member' will be resolved.
# noinspection PyProtectedMember
class SelectionTreeItems(object):
    def __init__(self, parent: "AugmentedTree"):
        self._parent = parent

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise NotImplementedError("Slicing is not supported ... yet.")
        item_row = self._parent._pathmap.iloc[index]
        items_real_path = item_row[AugmentedTree._COLNAME_REAL_PATH]
        parent_item = self._parent._all_parents_of_treeitems[items_real_path]
        items_access_key = item_row[AugmentedTree._COLNAME_PRIMEKEY]
        return parent_item.get_child(items_access_key)

    def __iter__(self):
        for index in range(len(self._parent._pathmap)):
            yield self[index]

    def print(self):
        index_for_getitem = 0
        for index, item_row in self._parent._pathmap.iterrows():
            items_real_path = item_row[AugmentedTree._COLNAME_REAL_PATH]
            items_augmented_path = item_row[AugmentedTree._COLNAME_AUGMENTED_PATH]
            parent = self._parent._all_parents_of_treeitems[items_real_path]
            tree_item = parent.get_child(item_row[AugmentedTree._COLNAME_PRIMEKEY])
            print("#{} {}".format(index_for_getitem, items_augmented_path))
            print_atree(tree_item, indent="  ", prefix="  ")
            index_for_getitem += 1


# noinspection PyProtectedMember
# The whole section regarding selection of tree items has to be reworked.
# By this measure the 'Access to a protected member' will be resolved.
class SelectionPaths(object):
    def __init__(self, parent: "AugmentedTree"):
        self._parent = parent

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise NotImplementedError("Slicing is not supported ... yet.")
        item_row = self._parent._pathmap.iloc[index]
        items_real_path = item_row[AugmentedTree._COLNAME_REAL_PATH]
        items_augmented_path = item_row[AugmentedTree._COLNAME_AUGMENTED_PATH]
        items_meta_attributes = item_row[AugmentedTree._COLNAME_META_ATTRIBUTES]
        items_meta_attributes = items_meta_attributes.split(TreePath.DELIMITER)
        treepath = TreePath(
            items_real_path, items_augmented_path, items_meta_attributes
        )
        return treepath


class AugmentedTree(AnAugmentedTreeItem):
    """
    This class is the recommended entry for augmenting nested data.

    Args:
        data(Union[Mapping, Sequence]):
            Augments this given data.

        use_schemas(bool):
            As default registered schemas are used. If turned to
            `false` this tree will represent the pure data
            structure.
    """

    ASSOCIATION_DELIMITER = "/"
    _COLNAME_REAL_PATH = "real_path"
    _COLNAME_AUGMENTED_PATH = "augmented_path"
    _COLNAME_META_ATTRIBUTES = "meta_attributes"
    _COLNAME_REAL_KEY = "real_key"
    _COLNAME_PRIMEKEY = "primekey"

    def __init__(
        self,
        data: Union[AnAugmentedCollection, Mapping, Sequence],
        use_schemas: bool = True,
        pathmap: DataFrame = None,
        treeitems_parents: Dict[str, AnAugmentedCollection] = None,
    ):
        """
        Augments the given `data`.

        Args:
            data(Union[Mapping, Sequence]):
                Augments this given data.

            use_schemas(bool):
                As default registered schemas are used. If turned to
                `false` this tree will represent the pure data
                structure.

            pathmap(DataFrame, optional):
                If given this map resembles the selected items of this
                tree.

            treeitems_parents(Dict[str, optional]):
                If given these items resembles the selection of this
                tree.
        """
        if isinstance(data, AnAugmentedCollection):
            augmented_treeitem = data
        else:
            augmented_treeitem = augment_datastructure(data, use_schemas=use_schemas)

        if treeitems_parents is None:
            self._all_parents_of_treeitems: Dict[str, AnAugmentedCollection] = {}
        else:
            self._all_parents_of_treeitems: Dict[
                str, AnAugmentedCollection
            ] = treeitems_parents

        self._is_in_selectionmode = False
        self._augmentedtree: AnAugmentedCollection = augmented_treeitem
        self._pathmap: DataFrame = pathmap
        self.using_schemas: bool = use_schemas
        self._pathmap_columnnames = [
            AugmentedTree._COLNAME_REAL_PATH,
            AugmentedTree._COLNAME_AUGMENTED_PATH,
            AugmentedTree._COLNAME_META_ATTRIBUTES,
            AugmentedTree._COLNAME_REAL_KEY,
            AugmentedTree._COLNAME_PRIMEKEY,
        ]
        self.missing_paths_of_queries = []
        self._selections = []
        if pathmap is None:
            self.map()
        self.treeitems = TreeItems(self)

    @property
    def parent(self) -> Optional["AnAugmentedCollection"]:
        return None

    @parent.setter
    def parent(self, parent):
        raise NotSupportedError(
            "An AugmentedTree cannot have a parent. Its the root."
            "This property setter should not have been called."
        )

    def collect_missing_query_results(self):
        result = self.missing_paths_of_queries.copy()
        for selection in self._selections:
            subresults = selection.collect_missing_query_results()
            result.extend(subresults)
        return result

    def register_failed_query(self, query: RegexPathQuery):
        self.missing_paths_of_queries.append(query)

    def __enter__(self):
        self._is_in_selectionmode = True
        self._selections.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_in_selectionmode = False
        for selection in self._selections:
            subresults = selection.collect_missing_query_results()
            self.missing_paths_of_queries.extend(subresults)

    def start_selecting(self):
        return self

    @property
    def all_selections_succeeded(self) -> bool:
        return len(self.missing_paths_of_queries) == 0

    def data(self, column: [int, str]) -> Any:
        try:
            return self._augmentedtree.data(column)
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    @property
    def primekey(self):
        try:
            return self._augmentedtree.primekey
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    @property
    def primename(self):
        try:
            return self._augmentedtree.primename
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    @property
    def primevalue(self):
        try:
            return self._augmentedtree.primevalue
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    @property
    def real_key(self):
        try:
            return self._augmentedtree.real_key
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    def iter_children(self,) -> Generator[AnAugmentedTreeItem, None, None]:
        try:
            for child in self._augmentedtree.iter_children():
                yield child
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    @property
    def children(self) -> Sequence:
        try:
            return self._augmentedtree.children
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    def insert_child_at(self, position, child):
        try:
            return self._augmentedtree.insert_child_at(position, child)
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    def has_primekey(self, key):
        try:
            return self._augmentedtree.has_primekey(key)
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    def get_child(self, primary_key):
        try:
            return self._augmentedtree.get_child(primary_key)
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    def children_count(self) -> int:
        try:
            return self._augmentedtree.children_count()
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    @property
    def leaf_type(self):
        try:
            return self._augmentedtree.leaf_type
        except AttributeError:
            raise ValueError("AugmentedTree doesn't have proper data.")

    def __bool__(self):
        return self._pathmap.empty

    def __iter__(self) -> Generator[Any, None, None]:
        for item in self._augmentedtree:
            yield item

    def __getitem__(self, index_or_key: Union[int, str]):
        if TreePath.DELIMITER in index_or_key:
            value = self.select(index_or_key)[0]
            return value
        return self._augmentedtree[index_or_key]

    def __setitem__(self, index_or_key: Union[int, str], value: Any):
        self._augmentedtree[index_or_key] = value

    def _select(
        self,
        *search_parts: List[Union[str, UnixFilePatternPart, RegularExpressionPart]],
        target_column_name: Optional[str] = None
    ) -> "AugmentedItemSelection":
        assert target_column_name is not None, "target_column_name cannot be None."
        query = RegexPathQuery(search_parts)
        indexes = self._pathmap[target_column_name].str.match(query.search_pattern)
        selected_map = self._pathmap[indexes]
        if selected_map.empty:
            self.register_failed_query(query)
        selected_items = {}
        for real_path in selected_map[self._COLNAME_REAL_PATH]:
            selected_items[real_path] = self._all_parents_of_treeitems[real_path]
        selection = AugmentedItemSelection(
            data=self._augmentedtree,
            pathmap=selected_map,
            treeitems_parents=selected_items,
            query=query,
        )
        self._selections.append(selection)
        return selection

    def select(self, *search_parts) -> "AugmentedTree":
        """
        Selects the tree items.

        Args:
            *search_parts:
                Path parts which should be selected.

        Returns:
            AugmentedTree:
                Model reduced to the selection.
        """
        clean_search_parts = []
        for search_part in search_parts:
            if isinstance(search_part, (list, tuple)):
                clean_part = UnixFilePatternPart(*search_part)
            else:
                clean_part = search_part
            clean_search_parts.append(clean_part)
        return self._select(
            *clean_search_parts,
            target_column_name=AugmentedTree._COLNAME_AUGMENTED_PATH
        )

    def where(self, *search_parts):
        return self._select(
            *search_parts, target_column_name=AugmentedTree._COLNAME_META_ATTRIBUTES
        )

    def map(self):
        treepaths_n_parent_treeitems = self._augmentedtree.get_pathmap()
        data_of_mapping_frame = []
        for treepath, parent_treeitem in treepaths_n_parent_treeitems:
            real_item_path = treepath.real_path
            augmented_item_path = treepath.augmented_path
            real_item_path = real_item_path.replace("/" + AUGMENTATION_ROOT_KEY, "")
            augmented_item_path = augmented_item_path.replace(
                "/" + AUGMENTATION_ROOT_KEY, ""
            )
            meta_attribute_items = [str(item) for item in treepath.meta_attributes]
            meta_attribute = self.ASSOCIATION_DELIMITER.join(meta_attribute_items)
            meta_attribute = self.ASSOCIATION_DELIMITER + meta_attribute
            items_primekey = treepath.primekey
            items_real_key = treepath.real_key
            items_data = [
                real_item_path,
                augmented_item_path,
                meta_attribute,
                items_real_key,
                items_primekey,
            ]
            data_of_mapping_frame.append(items_data)
            self._all_parents_of_treeitems[real_item_path] = parent_treeitem
        self._pathmap = DataFrame(
            data_of_mapping_frame, columns=self._pathmap_columnnames
        )

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._augmentedtree.primevalue)

    def print(self, additional_columns: List = None, show_hidden: bool = False):
        print_atree(
            treeitem=self._augmentedtree,
            additional_columns=additional_columns,
            show_hidden=show_hidden,
        )


class AugmentedItemSelection(AugmentedTree):
    def __init__(
        self,
        data: Union[AnAugmentedCollection, Mapping, Sequence],
        use_schemas: bool = True,
        pathmap: DataFrame = None,
        treeitems_parents: Dict[str, AnAugmentedCollection] = None,
        query: RegexPathQuery = None,
    ):
        """
        Augments the given `data`.

        Args:
            data(Union[Mapping, Sequence]):
                Augments this given data.

            use_schemas(bool):
                As default registered schemas are used. If turned to
                `false` this tree will represent the pure data
                structure.

            pathmap(DataFrame, optional):
                If given this map resembles the selected items of this
                tree.

            treeitems_parents(Dict[str, optional]):
                If given these items resembles the selection of this
                tree.
        """
        super().__init__(
            data=data,
            use_schemas=use_schemas,
            pathmap=pathmap,
            treeitems_parents=treeitems_parents,
        )
        self.treeitems = SelectionTreeItems(self)
        self.query = query
        self.paths = SelectionPaths(self)

    def empty(self):
        return len(self._pathmap) == 0

    def __getitem__(self, index):
        if self.empty():
            return None
        if isinstance(index, slice):
            selected_frame = self._pathmap.iloc[index]
            selected_items = []
            for index, item_row in selected_frame.iterrows():
                parent_treeitem = self._all_parents_of_treeitems[item_row.real_path]
                items_access_key = item_row[self._COLNAME_PRIMEKEY]
                selected_treeitem = parent_treeitem[items_access_key]
                selected_items.append(selected_treeitem)
            return selected_items
        item_row = self._pathmap.iloc[index]
        parent_treeitem = self._all_parents_of_treeitems[item_row.real_path]
        items_access_key = item_row[self._COLNAME_PRIMEKEY]
        selected_treeitem = parent_treeitem[items_access_key]
        return selected_treeitem

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            selected_frame = self._pathmap.iloc[index]
            for index, item_row in selected_frame.iterrows():
                parent_treeitem = self._all_parents_of_treeitems[item_row.real_path]
                items_access_key = item_row[self._COLNAME_PRIMEKEY]
                parent_treeitem[items_access_key] = value
            return
        item_row = self._pathmap.iloc[index]
        parent_treeitem = self._all_parents_of_treeitems[item_row.real_path]
        items_access_key = item_row[self._COLNAME_PRIMEKEY]
        parent_treeitem[items_access_key] = value

    def __str__(self):
        return self.query.search_pattern

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.query.search_pattern)

    def print(self, **kwargs):
        index_for_getitem = 0
        for index, item_row in self._pathmap.iterrows():
            items_real_path = item_row[AugmentedTree._COLNAME_REAL_PATH]
            parent_item = self._all_parents_of_treeitems[items_real_path]
            primekey = item_row[AugmentedTree._COLNAME_PRIMEKEY]
            child = parent_item.get_child(primekey)
            print("#{} {}".format(index_for_getitem, child.primevalue))
            index_for_getitem += 1
