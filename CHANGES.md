# Revision History

## 1.0 (2016/05/22)

- Initial stable release.

## 0.8.1 (2016/04/28)

- Now invoking `__init__` in `Dictionary` converters to run custom validations.

## 0.8 (2016/04/14)

- Replaced all utility functions with ORM-like tools.
- Removed the ability to check for existing files in `sync()`.
- Renamed and consolidated custom exceptions.
- Renamed sync parameter `auto=True` to `auto_save=True`.
- Renamed sync parameter `strict=True` to `auto_track=False`.
- Added sync parameter `auto_create` to defer file creation to ORM functions.

## 0.7.2 (2016/03/30)

- Now preserving order of `attr` decorators on `Dictionary` converters.

## 0.7.1 (2016/03/30)

- Updated `String` to fetch `true` and `false` as strings.

## 0.7 (2016/03/29)

- Now preserving order of `attr` decorators.
- Now limiting `attr` decorator to a single argument.
- Added `List.of_type()` factory to create lists with less boilerplate.

## 0.6.1 (2015/02/23)

- Fixed handling of `None` in `NullableString`.

## 0.6 (2015/02/23)

- Added preliminary support for JSON serialization (@pr0xmeh).
- Renamed `yorm.converters` to `yorm.types`.
- Now maintaining the signature on mapped objects.
- Disabled attribute inference unless `strict=False`.
- Fixed formatting of `String` to only use quotes if absolutely necessary.

## 0.5 (2015/09/25)

- Renamed `yorm.base` to `yorm.bases`.
- Stopped creating files on instantiation when `auto=False`.
- Now automatically storing on fetch after initial store.

## 0.4.1 (2015/06/19)

- Fixed attribute loss in non-`dict` when conversion to `dict`.
- Now automatically adding missing attributes to mapped objects.

## 0.4 (2015/05/16)

- Moved all converters into the `yorm.converters` package.
- Renamed `container` to `containers`.
- Renamed `Converter` to `Convertible` for mutable types
- Added a new `Converter` class for immutable types
- Removed the context manager in mapped objects.
- Fixed automatic mapping of nested attributes.

## 0.3.2 (2015/04/07)

- Fixed object overwrite when calling `utilities.update`.

## 0.3.1 (2015/04/06)

- Fixed infinite recursion with properties that rely on other mapped attributes.

## 0.3 (2015/03/10)

- Updated mapped objects to only read from the filesystem if there are changes.
- Renamed `store` to `sync_object`.
- Renamed `store_instances` to `sync_instances`.
- Renamed `map_attr` to `attr`.
- Added `sync` to call `sync_object` or `sync_instances` as needed.
- Added `update_object` and `update_file` to force synchronization.
- Added `update` to call `update_object` and/or `update_file` as needed.

## 0.2.1 (2015/02/12)

- Container types now extend their builtin type.
- Added `None<Type>` extended types with `None` as a default.
- Added `AttributeDictionary` with keys available as attributes.
- Added `SortedList` that sorts when dumped.

## 0.2 (2014/11/30)

- Allowing `map_attr` and `store` to be used together.
- Allowing `Dictionary` containers to be used as attributes.
- Fixed method resolution order for modified classes.
- Added a `yorm.settings.fake` option to bypass the filesystem.

## 0.1.1 (2014/10/20)

- Fixed typos in examples.

## 0.1 (2014/09/29)

 - Initial release.
