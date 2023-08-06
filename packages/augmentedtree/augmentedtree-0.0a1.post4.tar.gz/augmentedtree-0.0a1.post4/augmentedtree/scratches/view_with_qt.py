from typing import List, Generator, Any, Union, Tuple

from abc import ABC, abstractmethod

from augmentedtree import MappingTreeItem, SequenceTreeItem, ValueTreeItem, \
    augment_datastructure, get_augmentation_classes

from augmentedtree.core import PRIMARYKEY_KEY, PRIMARYNAME_KEY, PRIMARYVALUE_KEY, \
    ATreeItem, NotSupportedError


class QtTreeviewViewable(ABC):
    """
    Abstract tree item which aims for a compatibility with QT.
    """

    # convinient for QT
    @property
    @abstractmethod
    def Children(
        self,
    ) -> Generator["QtTreeviewViewable", "QtTreeviewViewable", "QtTreeviewViewable"]:
        """
        Iterates through the child-treeitems. Basic implementation for
        QT.

        Returns:
            QtTreeviewViewable: Child of this element.
        """
        pass

    # basic implementation for QT
    @abstractmethod
    def addChild(self, child):
        """
        Adding a child to this Element.

        Args:
            child (ATreeItem): Child to be added to this element.
        """
        pass

    # basic implementation for QT
    @property
    @abstractmethod
    def RowIndex(self) -> int:
        """
        Returning the integer index of this item within the parent.

        Returns:
            int: Index
        """
        pass

    # basic implementation for QT
    @abstractmethod
    def childrenCount(self) -> int:
        """
        Returning the childrens' count

        Returns:
            int: Count of children.
        """
        pass

    # basic implementation for QT
    @abstractmethod
    def getChildByIndex(self, index: int) -> Any:
        """
        Returns the child by its index within its parent.

        Args:
            index (int): Index (rowindex) of the child to be returned.

        Returns:
            Any: Child
        """
        pass

    # basic implementation for QT
    @abstractmethod
    def indexOfChild(self, child: Any):
        """
        Returns the child's index within its parent.

        Args:
            child (Any): Child for which the index should be returned.

        Returns:
            int: Child's index.
        """
        pass

    # basic implementation for QT
    @abstractmethod
    def data(self, column: int) -> Tuple[Union[int, str], Any]:
        """
        Returning a tuple for the given index.

        Args:
            column (int): (key or index, value) pair to be returned for the
                requested position within this sequence.

        Returns:
            Tuple[Union[int, str], Any]: Tuple of the `index` and
                `value`. The index might be a integer or str, while the
                `value` can be anything.
        """
        pass


class QtTreeviewEditable(ABC):
    # for editable tree in QT
    @abstractmethod
    def setData(self, column: str, value) -> bool:
        pass

    # convinient for QT
    @property
    @abstractmethod
    def Children(
        self,
    ) -> Generator["QtTreeviewViewable", "QtTreeviewViewable", "QtTreeviewViewable"]:
        """
        Iterates through the child-treeitems.

        Returns:
            QtTreeviewViewable: Child of this element.
        """
        pass

    # basic implementation for QT
    @abstractmethod
    def hasChildren(self) -> bool:
        pass

    # for editable tree in QT
    @abstractmethod
    def insertChildren(
        self,
        position: int,
        children: Union["QtTreeviewViewable", List["QtTreeviewViewable"]],
    ) -> bool:
        """
        Inserts a list of children into this tree element.

        Args:
            position(int): Position at which the children should be inserted.
            children(List[QtTreeviewViewable]: Children to be inserted into this element.

        Returns:
            bool: Returns a bool for the insertion success.
        """
        pass

    # for editable tree in QT
    # dependend on type; enable QT treeview
    @abstractmethod
    def removeChildren(self, position, count):
        pass

    # convinient method for QT treeview
    @abstractmethod
    def removeAllChildren(self):
        pass

    # convinient method for editable QT tree
    @abstractmethod
    def changeChildKey(self, oldkey, newkey) -> bool:
        """
        Changes the key of the child at `oldkey` with `newkey`.

        Args:
            oldkey(Union[str, int]): Old key where the current item is.
            newkey(Union[str, int]): New key of the old item.

        Returns:
            bool: Success of key change.
        """
        pass


class AQtTreeItem(QtTreeviewViewable, QtTreeviewEditable, ABC):
    pass


class QValueTreeItem(ValueTreeItem, QtTreeviewViewable, QtTreeviewEditable):
    def __init__(self, primarykey=None):
        super().__init__(primarykey=primarykey)

    def addChild(self, child):
        raise NotSupportedError(
            "A leaf cannot has children. This method should not have been called."
        )

    def RowIndex(self) -> int:
        assert (
            self.parent is not None
        ), "This element should has a parent. This method should not have been called."
        return self.parent.indexOfChild(self)

    def childrenCount(self) -> int:
        # important; no other child related methods should be called.
        return 0

    def getChildByIndex(self, index):
        raise NotSupportedError(
            "A leaf does not has children. This method should not have been called."
        )

    def indexOfChild(self, child):
        raise NotSupportedError(
            "A leaf does not has children. This method should not have been called."
        )

    def setData(self, column: str, value) -> bool:
        if column == PRIMARYKEY_KEY:
            assert self.parent is not None, "This element should have a parent."
            success = self.parent.changeChildKey(self.primekey, value)
            self._data[PRIMARYKEY_KEY] = value
            return success
        if column in (PRIMARYNAME_KEY, PRIMARYVALUE_KEY):
            self.parent[self.primekey] = value
            success = self.parent[self.primekey] == value
            return success
        return False

    @property
    def children(
        self
    ) -> Generator["QtTreeviewViewable", "QtTreeviewViewable", "QtTreeviewViewable"]:
        # important; no other child related methods should be called.
        return iter([])

    def hasChildren(self) -> bool:
        # important; no other child related methods should be called.
        return False

    def insertChildren(self, position, children: list):
        raise NotSupportedError(
            "A leaf cannot has children. This method should not have been called."
        )

    def removeChildren(self, position, count):
        raise NotSupportedError(
            "A leaf does not has children. This method should not have been called."
        )

    def removeAllChildren(self):
        raise NotSupportedError(
            "This item does not support children."
            "This method should not have been called."
        )

    def changeChildKey(self, oldkey, newkey):
        raise NotSupportedError(
            "This item does not support children."
            "This method should not have been called."
        )


class QSequenceTreeItem(SequenceTreeItem, QtTreeviewViewable, QtTreeviewEditable):
    """
    Dieses ``TreeItem`` hat die Ziele:

    - verschachtelte ``dict`` (Mapping) zu enthalten, welche Listen enthalten
      (Sequences) können, welche ebenfalls ``dict`` als Elemente haben können.
    - zusätzliche Einträge/Information zu den einzelnen Werten ermöglichen.
    """

    def __init__(
        self, primarykey_key: str = None, primaryvalue_key: Union[List, tuple] = None
    ):
        super().__init__(primarykey_key, primaryvalue_key)
        self._augemtationclasses = get_augmentation_classes("qt")

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self._data[PRIMARYVALUE_KEY])

    def addChild(self, child):
        self._children.append(child)
        child.parent = self

    @property
    def RowIndex(self) -> int:
        pass

    def childrenCount(self) -> int:
        return len(self._children)

    def getChildByIndex(self, index: int) -> Any:
        return self._children[index]

    def indexOfChild(self, child: Any):
        return self._children.index(child)

    def setData(self, column: str, value) -> bool:
        pass

    def hasChildren(self) -> bool:
        return len(self._children) > 0

    def insertChildren(
        self,
        position: int,
        children: Union["QtTreeviewViewable", List["QtTreeviewViewable"]],
    ) -> bool:
        raise NotImplementedError("not yet by {}".format(self.__class__.__name__))

    def removeChildren(self, position, count):
        raise NotImplementedError("not yet by {}".format(self.__class__.__name__))

    def removeAllChildren(self):
        raise NotImplementedError("not yet by {}".format(self.__class__.__name__))

    # dependend on type; enable QT treeview
    def changeChildKey(self, oldkey, newkey) -> bool:
        assert (
            oldkey not in self._data[PRIMARYVALUE_KEY]
        ), "{} should have been in data.".format(oldkey)
        olditem = self._data[PRIMARYVALUE_KEY][oldkey]
        self._data[PRIMARYVALUE_KEY][newkey] = olditem
        del self._data[PRIMARYVALUE_KEY][oldkey]
        childindex = self._childrenskeys.index(oldkey)
        child = self.getChildByIndex(childindex)
        child.primekey = newkey
        return True


class QMappingTreeItem(MappingTreeItem, QtTreeviewViewable, QtTreeviewEditable):
    def __init__(
        self,
        primarykey=None,
        primaryname=None,
        primaryvalue=None,
        outervaluekey=None,
        metadatakeys=None,
    ):
        super().__init__(
            primarykey, primaryname, primaryvalue, outervaluekey, metadatakeys
        )
        self._augmentationclasses = get_augmentation_classes("qt")

    def addChild(self, child: ATreeItem):
        raise NotImplementedError("not implemented yet")
        if child.primekey in self._children:
            raise KeyError("Key already exists. Cannot add child with same key.")
        self._children[child.key] = child
        child.parent = self

    @property
    def RowIndex(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.indexOfChild(self)

    def childrenCount(self, *args) -> int:
        return len(self._children)

    def getChildByIndex(self, index: int) -> Any:
        key = self._childrenskeys[index]
        return self._children[key]

    def indexOfChild(self, child: Any) -> int:
        # Here `_childrenskeys` should be used, since it stores the order
        return self._childrenskeys.index(child.primekey)

    # dependend on type; enable QT treeview
    def setData(self, column: str, value) -> Any:
        try:
            if column == PRIMARYKEY_KEY:
                # if the link is able to change its value, this means the link has not
                # the value `PRIMARYKEY_KEY` and points to this item's metadata
                if self._primarykeylink.change_value_of_key(value):
                    return True
                # else the `PrimeKey` has to be changed at the parent and if this
                # succed, then the new link can be set.
                if self.parent is None:
                    return False
                success = self.parent.changeChildKey(self.primekey, value)
                if success:
                    self._data[PRIMARYKEY_KEY] = value
                return success
            # The primary name and value of a mapping item cannot be changed.
            if column in (PRIMARYNAME_KEY, PRIMARYVALUE_KEY):
                return False
            return False
        except KeyError:
            return False
        except TypeError:
            return False

    def hasChildren(self):
        return len(self._children) > 0

    # for editable tree in QT
    def insertChildren(
        self,
        position: int,
        children: Union["QtTreeviewViewable", List["QtTreeviewViewable"]],
    ) -> bool:
        raise NotImplementedError("not implemented yet")

    # for editable tree in QT
    # dependend on type; enable QT treeview
    def removeChildren(self, position, count):
        raise NotImplementedError("not implemented yet")

    # convinient method for QT treeview
    def removeAllChildren(self):
        raise NotImplementedError("not implemented yet")

    # dependend on type; enable QT treeview
    def changeChildKey(self, oldkey, newkey) -> bool:
        assert oldkey in self._outervalues, "{} should have been in data.".format(
            oldkey
        )
        childindex = self._childrenskeys.index(oldkey)
        self._childrenskeys[childindex] = newkey
        self._outervalues[newkey] = self._outervalues.pop(oldkey)
        self._children[newkey] = self._children.pop(oldkey)
        return True


class QTree(object):
    def __new__(cls, nesteddata: Union[dict, list]):
        return augment_datastructure(nesteddata, augmentclasses=get_augmentation_classes("qt"))


def tree_to_string(
    tree: QtTreeviewViewable,
    columns: List = [PRIMARYKEY_KEY, PRIMARYVALUE_KEY],
    indent="",
):
    result = ""
    values = [str(tree.data(key)) for key in columns]
    myvalues = ", ".join(values)
    result += "{}{}\n".format(indent, myvalues)
    for child in tree.children:
        result += tree_to_string(child, columns, indent + "  ")
    return result


def print_tree_items(tree: QtTreeviewViewable, columns: List = None, indent=""):
    newindent = indent
    if not tree.primekey is "__root__":
        if columns is not None:
            values = [str(tree.data(key)) for key in columns]
            result = ", ".join(values)
            print(
                "{}{}: {} <{}> {}".format(
                    indent,
                    tree.data(PRIMARYKEY_KEY),
                    tree.data(PRIMARYNAME_KEY),
                    tree.leaf_type,
                    result,
                )
            )
        else:
            print(
                "{}{}: {} <{}>".format(
                    indent,
                    tree.data(PRIMARYKEY_KEY),
                    tree.data(PRIMARYNAME_KEY),
                    tree.leaf_type,
                )
            )
        newindent = "  " + indent
    for child in tree.Children:
        print_tree_items(child, columns, newindent)
