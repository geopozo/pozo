from pozo.ood.exceptions import SelectorTypeError, SelectorError, NameConflictError
import pozo.ood.extra_selectors as s



## We need to keep track whether or not the output is sorted or not
## It will generally by sorted if a) there is only one selector b) the selector is not a dictionary
## We need to start store _items_by_id w/ position
## Changing and swapping position needs to reflect their change

strict_index = False
allow_name_conflicts = False
multiparent = False

class ObservingOrderedDictionary():

    # Needs to accept a custom indexer
    def __init__(self, *args, **kwargs):
        global strict_index
        global allow_name_conflicts
        self._strict_index = kwargs.pop('strict_index', strict_index)
        self._allow_name_conflicts = kwargs.pop('allow_name_conflicts', allow_name_conflicts)
        self._items_ordered = []
        self._items_by_name = {}
        self._items_by_id = {}


        super().__init__(*args, **kwargs)

    def set_strict(self):
        self._strict_index = True
    def unset_strict(self):
        self._strict_index = False

    def __len__(self):
        return len(self._items_ordered)

    def __iter__(self):
        self._iterator_index = 0
        return self

    def __next__(self):
        if self._iterator_index < len(self._items_ordered):
            ret = self._items_ordered[self._iterator_index]
            self._iterator_index += 1
            return ret
        raise StopIteration

    def _add_item_to_by_name(self, item, name=None): # do we have verify this?
        if name is None:
            name = item.get_name()
        if name in self._items_by_name:
            self._items_by_name[name].append(item)
        else:
            self._items_by_name[name] = [item]

    def _remove_item_from_by_name(self, item, name=None):
        if name is None:
            name=item.get_name()
        if name in self._items_by_name:
            self._items_by_name[name].remove(item)
            if len(self._items_by_name[name]) == 0:
                del self._items_by_name[name]

    def _child_options(self, child, **kwargs):
        old_name = kwargs.get('old_name', None)
        if old_name is not None and old_name in self._items_by_name:
            if not self._allow_name_conflicts and self._check_key(child.get_name()):
                raise NameConflictError(f"Name taken by other item in parent {self.get_name()} of id {id(self)}")
                return False
            if not isinstance(child.get_name(), str):
                raise TypeError(f"Parent {self.get_name()} will only accept children with string names")
        return True
        # TODO: check child name

    def _child_update(self, child, **kwargs):
        old_name = kwargs.get('old_name', None)
        if old_name is not None:
            self._remove_item_from_by_name(child, name=old_name)
            self._add_item_to_by_name(child)
        return True
        # if you change your name, you _have_ to tell your parent.
        # we could test every set_name() at runtime for calling this function
        # we could only allow only ChildObserved inherited classes (they could still hack)
        # we could also dig around to see if we have the child, and if our name matches the
        # current name

    def add_items(self, *items, **kwargs):
        position = kwargs.pop("position", len(self))
        position = position if position >= 0 else len(self)+position
        if not position == len(self) and not self._check_index(position):
            raise IndexError("Cannot supply a index out of range")
        if len(items) != len(set(items)):
            raise ValueError("Trying to add same item twice or more")
        for item in items:
            if id(item) in self._items_by_id:
                raise ValueError("Tried to add item that already exists.")
            elif not hasattr(item, "get_name"):
                raise TypeError("All elements added must have a get_name() function")
            elif not self._allow_name_conflicts and item.get_name() in self._items_by_name:
                raise NameConflictError(f"allow_name_conflict is False, this name already exists: {item.get_name()}")
            item._register_parents(self)
            item._deregister_parents(self) # testing! 1 2 3
        for i, item in enumerate(items):
            if isinstance(item, ChildObserved):
                item._register_parents(self)
            self._items_ordered.insert(position+i, item)
            self._add_item_to_by_name(item)
            self._items_by_id[id(item)] = item

    # Will throw IndexErrors if any number is out of range
    def _check_index(self, index, target = None): # TODO, this needs to allow negatives
        if target is None:
            target = self._items_ordered
        if isinstance(index, int):
            if abs(index) >= len(target):
                return False
        elif isinstance(index, slice):
            if index.start is not None:
                if not self._check_index(index.start): return False
            if index.stop is not None:
                if not self._check_index(index.stop-1): return False
        return True

    def _count_dictionary(self): 
        count = 0
        for v in self._items_by_name.values():
            count += len(v)
        return count

    # This should throw an error if name not in dictionary
    def _check_key(self, name):
        if name not in self._items_by_name:
            return False
        return True

    # Throws key/index errors
    def _get_items_by_name(self, name, index=slice(None)):
        if not self._check_key(name): return []
        if not self._check_index(index): return []
        items = self._items_by_name[name][index]
        if not isinstance(items, list):
            return [items]
        return items

    # Throws key/index errors
    def _get_items_by_slice(self, indices):
        if not self._check_index(indices): return []
        return self._items_ordered[indices]

    # Throws key/index errors
    def _get_item_by_index(self, index):
        if not self._check_index(index): return
        return self._items_ordered[index]

    # Can return an empty list if a) no selectors supplied or b) skip_bad=True.
    # If selector makes no sense (4.5), will still throw error.
    def get_items(self, *selectors, **kwargs):
        cap = kwargs.get('_cap', 0)
        index = kwargs.get('index', None)
        strict_index = kwargs.get('strict_index', self._strict_index)
        items = []
        if not selectors or selectors[0] is None:
            items = self._items_ordered
            selectors = []
        for i, selector in enumerate(selectors):
            if cap and len(items) >= cap: break
            new_items = None
            if isinstance(selector, int):
                new_items = [self._get_item_by_index(selector)]
            elif isinstance(selector, slice):
                new_items = self._get_items_by_slice(selector)
            elif isinstance(selector, str):
                if index:
                    new_items = self._get_items_by_name(selector, index)
                else:
                    new_items = self._get_items_by_name(selector)
            elif isinstance(selector, s.Selector):
                new_items = selector._process(self)
            else:
                raise SelectorTypeError("Selectors must of type: str, int, slice or a class from package selectors.")
            if new_items and len(new_items)>0:
                items.extend(new_items)
            elif strict_index:
                raise SelectorError(f"Selector {i} did not return any values. You can set strict_index=False to receive [] instead")
        if cap and len(items) > cap: items = items[0:cap]
        resulting_items_by_id = {}
        for item in items:
            if id(item) not in resulting_items_by_id:
                resulting_items_by_id[id(item)] = item
        sorted_items = []
        for ref_item in self._items_ordered:
            if id(ref_item) in resulting_items_by_id:
                sorted_items.append(ref_item)
        return sorted_items

    def get_item(self, selector, **kwargs):
        match = kwargs.get('match', 0)
        strict_index = kwargs.get('strict_index', self._strict_index)
        if "_cap" in kwargs: kwargs.pop("_cap")
        items = self.get_items(selector, _cap = match + 1, **kwargs)
        if len(items) <= match:
            if strict_index:
                raise SelectorError(f"Supplied match ({match}) >= len(results) ({len(items)})") from IndexError()
            return None
        return items[match]

    # Because we can't check to see if we've supplied a correct object type, we can only return true or false
    def has_item(self, selector):
        if selector is None: raise ValueError("has_item() not passed anything to check")
        try:
            self.get_item(selector, strict_index=True)
            return True
        except (SelectorError):
            return False

    # Can throw regular IndexError if one value of the keys is out of order
    def reorder_all_items(self, order): # take other selectors
        if not isinstance(order, list): raise TypeError("You must provide a list of selectors to reorder the items")
        positions_new = []
        for i, selector in enumerate(order):
            if isinstance(selector, int):
                positions_new.append(selector)
            else:
                positions_new.append(self._items_ordered.index(self.get_item(selector, strict_index=True)))
        if not ( len(set(positions_new)) == len(order) == len(positions_new) == len(set(order)) == len(self) ):
            raise SelectorError("You must provide a list of all objects by some selector.") from ValueError()
        self._items_ordered = [self._items_ordered[i] for i in positions_new]

    def move_items(self, *selectors, **kwargs):
        position = kwargs.pop("position", None)
        distance = kwargs.pop("distance", None)
        before = kwargs.pop("before", None)
        after = kwargs.pop("after", None)

        count_flags = bool(before) + bool(after) + bool(distance) + bool(position is not None)
        if count_flags != 1:
            raise ValueError("You must set ONE of 'position', 'distance', 'before', or 'after'")

        items = self.get_items(*selectors)
        if not items or len(items) == 0: return
        if position is not None: # set position specifically
            if not isinstance(position, int):
                raise TypeError("The position to move to must be an integer, follow array access syntax.")
            if position < 0: position = len(self) + position
            if position != len(self) and not self._check_index(position):
                raise IndexError("Position must be a valid index")
            if position != len(self):
                # rightmost items inserted first, they'll be pushed further right w/ each successive
                # insertion.
                # unless position == len(self), which is append()
                items = reversed(items)
            for item in items:
                original_index = self._items_ordered.index(item)
                self._items_ordered[original_index] = None # Don't change structure of list while playing with positions!
                self._items_ordered.insert(position, item) # TODO, can it take negatives?
                self._items_ordered.remove(None)
        elif isinstance(distance, int) and distance > 0: # Move to right
            distance += 1 # again, insert naturally puts you to the left of whatever was in the position you want
            wall = len(self) # We're moving to the right, so:
            for item in reversed(items): # Move rightmost items FIRST
                position = min(self._items_ordered.index(item) + distance, len(self)) # len is rightmost max
                if position > wall: position = wall # don't move farther right than and item that started farther right
                wall = position - 1
                self.move_items(item, position=position)
        elif isinstance(distance, int) and distance < 0: # Move to left
            wall = 0 # We're moving to the left
            for item in items: # move leftmost first
                position = max(self._items_ordered.index(item) + distance, 0) # Can't move farther left than 0
                if position < wall: position = wall # Shouldn't move father left than what started farther left
                wall = position + 1
                self.move_items(item, position=position)
        elif distance: # so do nothing if distance = 0
            raise TypeError("distance must be an integer")
        elif before: # Move items just before some item (this is exactly the same as position, to be honest)
            position = self._items_ordered.index(self.get_item(before, strict_index=True))
            self.move_items(*items, position=position)
        elif after: # It's before except +1
            position = self._items_ordered.index(self.get_item(after, strict_index=True)) + 1
            self.move_items(*items, position=position)

    def pop_items(self, *selectors, **kwargs):
        if not selectors or len(selectors)==0: return []
        items = self.get_items(*selectors, **kwargs)
        for item in items:
            item._deregister_parents(self)
            self._items_ordered.remove(item)
            self._remove_item_from_by_name(item)
            del self._items_by_id[id(item)]
        return items

class ChildObserved(s.Selector):

    def __init__(self, *args, **kwargs):
        global multiparent
        self._name = kwargs.pop('name', "unnamed")
        if not isinstance(self._name, str):
            raise TypeError("Name must be a string, please")
        self._multiparent = kwargs.pop('multiparent', multiparent)
        self._parents_by_id = {}

        super().__init__(*args, **kwargs)

    ## Sort of an odd function here- could make a _get_item_by_id but it's overkill.
    def _process(self, parent):
        if id(self) in parent._items_by_id:
            return [self]
        return []

    def get_name(self):
        return self._name

    def set_name(self, name):
        if self._name == name: return
        old_name = self._name
        self._name = name
        try:
            self._notify_parents(old_name=old_name)
        except Exception as e:
            self._name = old_name
            raise e

    def _register_parents(self, *parents):
        if not self._multiparent and (bool(len(self._parents_by_id)) or len(parents)>1):
            raise Exception("Tried to add child who already has a parent (or tried to add multiple parents). Set multiparent=True when creating children to override. Not recommended")
        for parent in parents:
            if id(parent) in self._parents_by_id: continue
            if not isinstance(parent, ObservingOrderedDictionary):
                raise ValueError("All parents must inhert ObservingOrderedDictionary class")
            self._parents_by_id[id(parent)] = parent


    def _deregister_parents(self, *parents):
        for parent in parents:
            if id(parent) in self._parents_by_id:
                del self._parents_by_id[id(parent)]

    def _get_parents(self):
        return list(self._parents_by_id.values())

    def _notify_parents(self, **kwargs):
        for parent in self._parents_by_id.values():
            if not parent._child_options(self, **kwargs):
                return False
        for parent in self._parents_by_id.values():
            if not parent._child_update(self, **kwargs):
                raise Exception("Fatal Error: Parent item changed mind about child update after giving permission. One of the parents of this item is unstable!")
        return True

