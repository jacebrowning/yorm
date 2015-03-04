Changelog
=========

0.3 (dev)
---------

- Updated mapped objects to only read from the filesystem if there are changes.
- Renamed `store` to `sync_object`.
- Renamed `store_instances` to `sync_instances`.
- Renamed `map_attr` to `attr`.
- Added `sync` to call `sync_object` or `sync_instances` as needed.
- Added `update_object` and `update_file` to force syncrhonization.
- Added `update` to call `update_object` and/or `update_file` as needed.

0.2.1 (2015-2-12)
-----------------

- Container types now extend their builtin type.
- Added `None<Type>` extended types with `None` as a default.
- Added `AttributeDictionary` with keys available as attributes.
- Added `SortedList` that sorts when dumped.

0.2 (2014-11-30)
----------------

- Allowing `map_attr` and `store` to be used together.
- Allowing `Dictionary` containers to be used as attributes.
- Fixed method resolution order for modified classes.
- Added a `yorm.settings.fake` option to bypass the filesystem.

0.1.1 (2014-10-20)
------------------

- Fixed typos in examples.

0.1 (2014-09-29)
----------------

 - Initial release.
