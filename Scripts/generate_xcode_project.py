#!/usr/bin/env python3

import os
import uuid
import shutil


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_NAME = "AsasecIl2cppDumper-Gui-App"
TARGET_NAME = "AsasecIl2cppDumper-Gui-App"

BUNDLE_IDENTIFIER = "com.asasec.Il2cppDumper"

APP_DIRECTORY = PROJECT_NAME
PROJECT_DIRECTORY = PROJECT_NAME + ".xcodeproj"

PROJECT_FILE = os.path.join(
    PROJECT_DIRECTORY,
    "project.pbxproj"
)

SOURCE_ROOT = APP_DIRECTORY


# ============================================================
# FILE TYPES
# ============================================================

SOURCE_TYPES = {
    ".swift": "sourcecode.swift",

    ".m": "sourcecode.c.objc",
    ".mm": "sourcecode.cpp.objcpp",

    ".c": "sourcecode.c.c",
    ".cc": "sourcecode.cpp.cpp",
    ".cpp": "sourcecode.cpp.cpp",
}

HEADER_TYPES = {
    ".h": "sourcecode.c.h",
    ".hh": "sourcecode.cpp.h",
    ".hpp": "sourcecode.cpp.h",
    ".hxx": "sourcecode.cpp.h",
}

RESOURCE_TYPES = {
    ".storyboard": "file.storyboard",
    ".xib": "file.xib",

    ".json": "text.json",
    ".strings": "text.plist.strings",

    ".metal": "sourcecode.metal",
}


# ============================================================
# UUID
# ============================================================

def make_uuid(value):

    return uuid.uuid5(
        uuid.NAMESPACE_URL,
        "asasec-xcode-project:" + value
    ).hex.upper()[:24]


# ============================================================
# HELPERS
# ============================================================

def normalize(path):

    return path.replace(
        os.sep,
        "/"
    )


def extension(path):

    return os.path.splitext(
        path
    )[1].lower()


def quote(value):

    if value is None:
        return '""'

    if any(
        character in value
        for character in [
            " ",
            "\t",
            "(",
            ")",
        ]
    ):

        return '"' + value + '"'

    return value


def is_source(path):

    return extension(path) in SOURCE_TYPES


def is_header(path):

    return extension(path) in HEADER_TYPES


def is_resource(path):

    return extension(path) in RESOURCE_TYPES


# ============================================================
# GROUP
# ============================================================

class Group:

    def __init__(
        self,
        group_id,
        name=None,
        path=None,
        parent=None,
        is_root=False
    ):

        self.id = group_id
        self.name = name
        self.path = path
        self.parent = parent
        self.is_root = is_root

        self.children = []


# ============================================================
# PROJECT DATA
# ============================================================

class PBXData:

    def __init__(self):

        # Main IDs
        self.project_id = make_uuid(
            "project:" + PROJECT_NAME
        )

        self.target_id = make_uuid(
            "target:" + TARGET_NAME
        )

        # Groups
        self.root_group_id = make_uuid(
            "group:root"
        )

        self.app_group_id = make_uuid(
            "group:" + APP_DIRECTORY
        )

        self.products_group_id = make_uuid(
            "group:Products"
        )

        # Build phases
        self.sources_phase_id = make_uuid(
            "sources:" + TARGET_NAME
        )

        self.frameworks_phase_id = make_uuid(
            "frameworks:" + TARGET_NAME
        )

        self.resources_phase_id = make_uuid(
            "resources:" + TARGET_NAME
        )

        # Project configuration
        self.project_config_list_id = make_uuid(
            "project-config:" + PROJECT_NAME
        )

        self.debug_project_config_id = make_uuid(
            "project-debug:" + PROJECT_NAME
        )

        self.release_project_config_id = make_uuid(
            "project-release:" + PROJECT_NAME
        )

        # Target configuration
        self.target_config_list_id = make_uuid(
            "target-config:" + TARGET_NAME
        )

        self.debug_target_config_id = make_uuid(
            "target-debug:" + TARGET_NAME
        )

        self.release_target_config_id = make_uuid(
            "target-release:" + TARGET_NAME
        )

        # File references
        self.file_references = []

        # Build files
        self.build_files = []

        # Source build files
        self.source_build_files = []

        # Resource build files
        self.resource_build_files = []

        # Groups
        self.root_group = None

        self.group_map = {}


# ============================================================
# SCAN
# ============================================================

def scan_project_files():

    result = []

    if not os.path.isdir(
        SOURCE_ROOT
    ):

        raise RuntimeError(
            "Kaynak klasörü bulunamadı: "
            + SOURCE_ROOT
        )

    for root, directories, filenames in os.walk(
        SOURCE_ROOT
    ):

        # Asset catalogların içine girme.
        directories[:] = [
            directory
            for directory in directories
            if not directory.endswith(".xcassets")
            and directory not in {
                ".git",
                "DerivedData",
                "build",
            }
        ]

        for filename in filenames:

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = normalize(
                os.path.relpath(
                    full_path,
                    SOURCE_ROOT
                )
            )

            # Info.plist kaynak olarak eklenmez.
            if filename == "Info.plist":
                continue

            # Asset catalog içerisindeki dosyalar
            # ayrıca eklenmez.
            if ".xcassets/" in relative_path:
                continue

            if (
                is_source(relative_path)
                or
                is_header(relative_path)
                or
                is_resource(relative_path)
            ):

                result.append(
                    relative_path
                )

    return sorted(result)


def scan_asset_catalogs():

    result = []

    for root, directories, filenames in os.walk(
        SOURCE_ROOT
    ):

        for directory in list(directories):

            if directory.endswith(
                ".xcassets"
            ):

                full_path = os.path.join(
                    root,
                    directory
                )

                relative_path = normalize(
                    os.path.relpath(
                        full_path,
                        SOURCE_ROOT
                    )
                )

                result.append(
                    relative_path
                )

                # İçine tekrar girme.
                directories.remove(
                    directory
                )

    return sorted(result)


# ============================================================
# GROUP TREE
# ============================================================

def create_group_tree(data):

    root = Group(
        data.root_group_id,
        is_root=True
    )

    app_group = Group(
        data.app_group_id,
        name=APP_DIRECTORY,
        path=APP_DIRECTORY,
        parent=root
    )

    products_group = Group(
        data.products_group_id,
        name="Products",
        path=None,
        parent=root
    )

    root.children.append(
        app_group
    )

    root.children.append(
        products_group
    )

    data.root_group = root

    data.group_map[""] = app_group

    return root


def ensure_group(
    data,
    directory
):

    if directory in data.group_map:

        return data.group_map[
            directory
        ]

    parent_directory = os.path.dirname(
        directory
    )

    parent_group = ensure_group(
        data,
        parent_directory
    )

    name = os.path.basename(
        directory
    )

    group_id = make_uuid(
        "group:" + directory
    )

    group = Group(
        group_id,
        name=name,
        path=name,
        parent=parent_group
    )

    parent_group.children.append(
        group
    )

    data.group_map[
        directory
    ] = group

    return group


# ============================================================
# ADD FILE
# ============================================================

def add_file(
    data,
    relative_path
):

    filename = os.path.basename(
        relative_path
    )

    ext = extension(
        relative_path
    )

    if ext in SOURCE_TYPES:

        file_type = SOURCE_TYPES[
            ext
        ]

        is_build_source = True
        is_build_resource = False

    elif ext in HEADER_TYPES:

        file_type = HEADER_TYPES[
            ext
        ]

        is_build_source = False
        is_build_resource = False

    elif ext in RESOURCE_TYPES:

        file_type = RESOURCE_TYPES[
            ext
        ]

        is_build_source = False
        is_build_resource = True

    else:

        return

    file_id = make_uuid(
        "file:" + relative_path
    )

    data.file_references.append(
        {
            "id": file_id,
            "name": filename,
            "path": relative_path,
            "type": file_type,
        }
    )

    group_path = os.path.dirname(
        relative_path
    )

    group = ensure_group(
        data,
        group_path
    )

    group.children.append(
        {
            "type": "file",
            "id": file_id,
            "name": filename,
        }
    )

    if is_build_source:

        build_id = make_uuid(
            "build:" + relative_path
        )

        data.build_files.append(
            {
                "id": build_id,
                "name": filename,
                "file_id": file_id,
                "phase": "Sources",
            }
        )

        data.source_build_files.append(
            build_id
        )

    elif is_build_resource:

        build_id = make_uuid(
            "build-resource:" + relative_path
        )

        data.build_files.append(
            {
                "id": build_id,
                "name": filename,
                "file_id": file_id,
                "phase": "Resources",
            }
        )

        data.resource_build_files.append(
            build_id
        )


# ============================================================
# ADD ASSET CATALOG
# ============================================================

def add_asset_catalog(
    data,
    relative_path
):

    filename = os.path.basename(
        relative_path
    )

    file_id = make_uuid(
        "asset:" + relative_path
    )

    build_id = make_uuid(
        "asset-build:" + relative_path
    )

    data.file_references.append(
        {
            "id": file_id,
            "name": filename,
            "path": relative_path,
            "type": "folder.assetcatalog",
        }
    )

    group_path = os.path.dirname(
        relative_path
    )

    group = ensure_group(
        data,
        group_path
    )

    group.children.append(
        {
            "type": "file",
            "id": file_id,
            "name": filename,
        }
    )

    data.build_files.append(
        {
            "id": build_id,
            "name": filename,
            "file_id": file_id,
            "phase": "Resources",
        }
    )

    data.resource_build_files.append(
        build_id
    )


# ============================================================
# GROUP OUTPUT
# ============================================================

def group_sort_key(child):

    if isinstance(
        child,
        Group
    ):

        return (
            0,
            (child.name or "").lower()
        )

    return (
        1,
        (child["name"] or "").lower()
    )


def generate_group(
    group,
    lines
):

    lines.append(
        "\t\t"
        + group.id
        + " = {"
    )

    lines.append(
        "\t\t\tisa = PBXGroup;"
    )

    lines.append(
        "\t\t\tchildren = ("
    )

    children = sorted(
        group.children,
        key=group_sort_key
    )

    for child in children:

        if isinstance(
            child,
            Group
        ):

            comment = child.name or "Group"

            lines.append(
                "\t\t\t\t"
                + child.id
                + " /* "
                + comment
                + " */,"
            )

        else:

            lines.append(
                "\t\t\t\t"
                + child["id"]
                + " /* "
                + child["name"]
                + " */,"
            )

    lines.append(
        "\t\t\t);"
    )

    # Root group kesinlikle path/name almaz.
    if not group.is_root:

        if group.name is not None:

            lines.append(
                "\t\t\tname = "
                + quote(group.name)
                + ";"
            )

        if group.path is not None:

            lines.append(
                "\t\t\tpath = "
                + quote(group.path)
                + ";"
            )

    lines.append(
        "\t\t\tsourceTree = \"<group>\";"
    )

    lines.append(
        "\t\t};"
    )

    lines.append("")

    for child in children:

        if isinstance(
            child,
            Group
        ):

            generate_group(
                child,
                lines
            )


# ============================================================
# BUILD FILE NAME
# ============================================================

def build_file_name(
    data,
    build_id
):

    for item in data.build_files:

        if item["id"] == build_id:

            return item["name"]

    return "Unknown"


# ============================================================
# GENERATE PROJECT
# ============================================================

def generate_project():

    data = PBXData()

    create_group_tree(
        data
    )

    files = scan_project_files()

    assets = scan_asset_catalogs()

    for relative_path in files:

        add_file(
            data,
            relative_path
        )

    for relative_path in assets:

        add_asset_catalog(
            data,
            relative_path
        )

    # ========================================================
    # PRODUCT
    # ========================================================

    product_file_id = make_uuid(
        "product:" + TARGET_NAME
    )

    data.file_references.append(
        {
            "id": product_file_id,
            "name": TARGET_NAME + ".app",
            "path": TARGET_NAME + ".app",
            "type": "wrapper.application",
            "product": True,
        }
    )

    products_group = None

    for child in data.root_group.children:

        if (
            isinstance(child, Group)
            and
            child.id == data.products_group_id
        ):

            products_group = child

            break

    products_group.children.append(
        {
            "type": "file",
            "id": product_file_id,
            "name": TARGET_NAME + ".app",
        }
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    lines = []

    lines.append(
        "// !$*UTF8*$!"
    )

    lines.append(
        "{"
    )

    lines.append(
        "\tarchiveVersion = 1;"
    )

    lines.append(
        "\tclasses = {"
    )

    lines.append(
        "\t};"
    )

    lines.append(
        "\tobjectVersion = 56;"
    )

    lines.append(
        "\tobjects = {"
    )

    lines.append("")

    # ========================================================
    # PBXBuildFile
    # ========================================================

    lines.append(
        "/* Begin PBXBuildFile section */"
    )

    for item in data.build_files:

        lines.append(
            "\t\t"
            + item["id"]
            + " /* "
            + item["name"]
            + " in "
            + item["phase"]
            + " */ = {"
        )

        lines.append(
            "\t\t\tisa = PBXBuildFile;"
        )

        lines.append(
            "\t\t\tfileRef = "
            + item["file_id"]
            + " /* "
            + item["name"]
            + " */;"
        )

        lines.append(
            "\t\t};"
        )

    lines.append(
        "/* End PBXBuildFile section */"
    )

    lines.append("")

    # ========================================================
    # PBXFileReference
    # ========================================================

    lines.append(
        "/* Begin PBXFileReference section */"
    )

    for item in data.file_references:

        lines.append(
            "\t\t"
            + item["id"]
            + " /* "
            + item["name"]
            + " */ = {"
        )

        lines.append(
            "\t\t\tisa = PBXFileReference;"
        )

        if item.get(
            "product",
            False
        ):

            lines.append(
                "\t\t\texplicitFileType = wrapper.application;"
            )

            lines.append(
                "\t\t\tincludeInIndex = 0;"
            )

            lines.append(
                "\t\t\tpath = "
                + quote(item["path"])
                + ";"
            )

            lines.append(
                "\t\t\tsourceTree = BUILT_PRODUCTS_DIR;"
            )

        else:

            lines.append(
                "\t\t\tlastKnownFileType = "
                + item["type"]
                + ";"
            )

            lines.append(
                "\t\t\tpath = "
                + quote(item["path"])
                + ";"
            )

            lines.append(
                "\t\t\tsourceTree = \"<group>\";"
            )

        lines.append(
            "\t\t};"
        )

    lines.append(
        "/* End PBXFileReference section */"
    )

    lines.append("")

    # ========================================================
    # PBXFrameworksBuildPhase
    # ========================================================

    lines.append(
        "/* Begin PBXFrameworksBuildPhase section */"
    )

    lines.append(
        "\t\t"
        + data.frameworks_phase_id
        + " /* Frameworks */ = {"
    )

    lines.append(
        "\t\t\tisa = PBXFrameworksBuildPhase;"
    )

    lines.append(
        "\t\t\tbuildActionMask = 2147483647;"
    )

    lines.append(
        "\t\t\tfiles = ("
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\trunOnlyForDeploymentPostprocessing = 0;"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End PBXFrameworksBuildPhase section */"
    )

    lines.append("")

    # ========================================================
    # PBXGroup
    # ========================================================

    lines.append(
        "/* Begin PBXGroup section */"
    )

    generate_group(
        data.root_group,
        lines
    )

    lines.append(
        "/* End PBXGroup section */"
    )

    lines.append("")

    # ========================================================
    # PBXNativeTarget
    # ========================================================

    lines.append(
        "/* Begin PBXNativeTarget section */"
    )

    lines.append(
        "\t\t"
        + data.target_id
        + " /* "
        + TARGET_NAME
        + " */ = {"
    )

    lines.append(
        "\t\t\tisa = PBXNativeTarget;"
    )

    lines.append(
        "\t\t\tbuildConfigurationList = "
        + data.target_config_list_id
        + " /* Build configuration list for PBXNativeTarget \""
        + TARGET_NAME
        + "\" */;"
    )

    lines.append(
        "\t\t\tbuildPhases = ("
    )

    lines.append(
        "\t\t\t\t"
        + data.sources_phase_id
        + " /* Sources */,"
    )

    lines.append(
        "\t\t\t\t"
        + data.frameworks_phase_id
        + " /* Frameworks */,"
    )

    lines.append(
        "\t\t\t\t"
        + data.resources_phase_id
        + " /* Resources */,"
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\tbuildRules = ("
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\tdependencies = ("
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\tname = "
        + quote(TARGET_NAME)
        + ";"
    )

    lines.append(
        "\t\t\tproductName = "
        + quote(TARGET_NAME)
        + ";"
    )

    lines.append(
        "\t\t\tproductReference = "
        + product_file_id
        + " /* "
        + TARGET_NAME
        + ".app */;"
    )

    lines.append(
        "\t\t\tproductType = \"com.apple.product-type.application\";"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End PBXNativeTarget section */"
    )

    lines.append("")

    # ========================================================
    # PBXProject
    # ========================================================

    lines.append(
        "/* Begin PBXProject section */"
    )

    lines.append(
        "\t\t"
        + data.project_id
        + " /* Project object */ = {"
    )

    lines.append(
        "\t\t\tisa = PBXProject;"
    )

    lines.append(
        "\t\t\tattributes = {"
    )

    lines.append(
        "\t\t\t\tLastUpgradeCheck = 1600;"
    )

    lines.append(
        "\t\t\t\tTargetAttributes = {"
    )

    lines.append(
        "\t\t\t\t\t"
        + data.target_id
        + " = {"
    )

    lines.append(
        "\t\t\t\t\t\tCreatedOnToolsVersion = 16.0;"
    )

    lines.append(
        "\t\t\t\t\t};"
    )

    lines.append(
        "\t\t\t\t};"
    )

    lines.append(
        "\t\t\t};"
    )

    lines.append(
        "\t\t\tbuildConfigurationList = "
        + data.project_config_list_id
        + " /* Build configuration list for PBXProject \""
        + PROJECT_NAME
        + "\" */;"
    )

    lines.append(
        "\t\t\tcompatibilityVersion = \"Xcode 14.0\";"
    )

    lines.append(
        "\t\t\tdevelopmentRegion = en;"
    )

    lines.append(
        "\t\t\thasScannedForEncodings = 0;"
    )

    lines.append(
        "\t\t\tknownRegions = ("
    )

    lines.append(
        "\t\t\t\ten,"
    )

    lines.append(
        "\t\t\t\tBase,"
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\tmainGroup = "
        + data.root_group_id
        + ";"
    )

    lines.append(
        "\t\t\tproductRefGroup = "
        + data.products_group_id
        + " /* Products */;"
    )

    lines.append(
        "\t\t\tprojectDirPath = \"\";"
    )

    lines.append(
        "\t\t\tprojectRoot = \"\";"
    )

    lines.append(
        "\t\t\ttargets = ("
    )

    lines.append(
        "\t\t\t\t"
        + data.target_id
        + " /* "
        + TARGET_NAME
        + " */,"
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End PBXProject section */"
    )

    lines.append("")

    # ========================================================
    # PBXResourcesBuildPhase
    # ========================================================

    lines.append(
        "/* Begin PBXResourcesBuildPhase section */"
    )

    lines.append(
        "\t\t"
        + data.resources_phase_id
        + " /* Resources */ = {"
    )

    lines.append(
        "\t\t\tisa = PBXResourcesBuildPhase;"
    )

    lines.append(
        "\t\t\tbuildActionMask = 2147483647;"
    )

    lines.append(
        "\t\t\tfiles = ("
    )

    for build_id in data.resource_build_files:

        filename = build_file_name(
            data,
            build_id
        )

        lines.append(
            "\t\t\t\t"
            + build_id
            + " /* "
            + filename
            + " in Resources */,"
        )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\trunOnlyForDeploymentPostprocessing = 0;"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End PBXResourcesBuildPhase section */"
    )

    lines.append("")

    # ========================================================
    # PBXSourcesBuildPhase
    # ========================================================

    lines.append(
        "/* Begin PBXSourcesBuildPhase section */"
    )

    lines.append(
        "\t\t"
        + data.sources_phase_id
        + " /* Sources */ = {"
    )

    lines.append(
        "\t\t\tisa = PBXSourcesBuildPhase;"
    )

    lines.append(
        "\t\t\tbuildActionMask = 2147483647;"
    )

    lines.append(
        "\t\t\tfiles = ("
    )

    for build_id in data.source_build_files:

        filename = build_file_name(
            data,
            build_id
        )

        lines.append(
            "\t\t\t\t"
            + build_id
            + " /* "
            + filename
            + " in Sources */,"
        )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\trunOnlyForDeploymentPostprocessing = 0;"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End PBXSourcesBuildPhase section */"
    )

    lines.append("")

    # ========================================================
    # XCBuildConfiguration
    # ========================================================

    lines.append(
        "/* Begin XCBuildConfiguration section */"
    )

    # --------------------------------------------------------
    # Project Debug
    # --------------------------------------------------------

    lines.append(
        "\t\t"
        + data.debug_project_config_id
        + " /* Debug */ = {"
    )

    lines.append(
        "\t\t\tisa = XCBuildConfiguration;"
    )

    lines.append(
        "\t\t\tbuildSettings = {"
    )

    lines.append(
        "\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;"
    )

    lines.append(
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;"
    )

    lines.append(
        "\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;"
    )

    lines.append(
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;"
    )

    lines.append(
        "\t\t\t\tSDKROOT = iphoneos;"
    )

    lines.append(
        "\t\t\t\tSWIFT_VERSION = 5.0;"
    )

    lines.append(
        "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";"
    )

    lines.append(
        "\t\t\t};"
    )

    lines.append(
        "\t\t\tname = Debug;"
    )

    lines.append(
        "\t\t};"
    )

    # --------------------------------------------------------
    # Project Release
    # --------------------------------------------------------

    lines.append(
        "\t\t"
        + data.release_project_config_id
        + " /* Release */ = {"
    )

    lines.append(
        "\t\t\tisa = XCBuildConfiguration;"
    )

    lines.append(
        "\t\t\tbuildSettings = {"
    )

    lines.append(
        "\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;"
    )

    lines.append(
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;"
    )

    lines.append(
        "\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;"
    )

    lines.append(
        "\t\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;"
    )

    lines.append(
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;"
    )

    lines.append(
        "\t\t\t\tSDKROOT = iphoneos;"
    )

    lines.append(
        "\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;"
    )

    lines.append(
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-O\";"
    )

    lines.append(
        "\t\t\t\tSWIFT_VERSION = 5.0;"
    )

    lines.append(
        "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";"
    )

    lines.append(
        "\t\t\t};"
    )

    lines.append(
        "\t\t\tname = Release;"
    )

    lines.append(
        "\t\t};"
    )

    # --------------------------------------------------------
    # Target Debug
    # --------------------------------------------------------

    lines.append(
        "\t\t"
        + data.debug_target_config_id
        + " /* Debug */ = {"
    )

    lines.append(
        "\t\t\tisa = XCBuildConfiguration;"
    )

    lines.append(
        "\t\t\tbuildSettings = {"
    )

    lines.append(
        "\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;"
    )

    lines.append(
        "\t\t\t\tCODE_SIGNING_ALLOWED = NO;"
    )

    lines.append(
        "\t\t\t\tCODE_SIGNING_REQUIRED = NO;"
    )

    lines.append(
        "\t\t\t\tCODE_SIGN_IDENTITY = \"\";"
    )

    lines.append(
        "\t\t\t\tDEVELOPMENT_TEAM = \"\";"
    )

    lines.append(
        "\t\t\t\tGENERATE_INFOPLIST_FILE = NO;"
    )

    lines.append(
        "\t\t\t\tINFOPLIST_FILE = \""
        + APP_DIRECTORY
        + "/Info.plist\";"
    )

    lines.append(
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;"
    )

    lines.append(
        "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \""
        + BUNDLE_IDENTIFIER
        + "\";"
    )

    lines.append(
        "\t\t\t\tPRODUCT_NAME = \""
        + TARGET_NAME
        + "\";"
    )

    lines.append(
        "\t\t\t\tSWIFT_VERSION = 5.0;"
    )

    lines.append(
        "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";"
    )

    lines.append(
        "\t\t\t};"
    )

    lines.append(
        "\t\t\tname = Debug;"
    )

    lines.append(
        "\t\t};"
    )

    # --------------------------------------------------------
    # Target Release
    # --------------------------------------------------------

    lines.append(
        "\t\t"
        + data.release_target_config_id
        + " /* Release */ = {"
    )

    lines.append(
        "\t\t\tisa = XCBuildConfiguration;"
    )

    lines.append(
        "\t\t\tbuildSettings = {"
    )

    lines.append(
        "\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;"
    )

    lines.append(
        "\t\t\t\tCODE_SIGNING_ALLOWED = NO;"
    )

    lines.append(
        "\t\t\t\tCODE_SIGNING_REQUIRED = NO;"
    )

    lines.append(
        "\t\t\t\tCODE_SIGN_IDENTITY = \"\";"
    )

    lines.append(
        "\t\t\t\tDEVELOPMENT_TEAM = \"\";"
    )

    lines.append(
        "\t\t\t\tDEVELOPMENT_TEAM = \"\";"
    )

    lines.append(
        "\t\t\t\tGENERATE_INFOPLIST_FILE = NO;"
    )

    lines.append(
        "\t\t\t\tINFOPLIST_FILE = \""
        + APP_DIRECTORY
        + "/Info.plist\";"
    )

    lines.append(
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;"
    )

    lines.append(
        "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = \""
        + BUNDLE_IDENTIFIER
        + "\";"
    )

    lines.append(
        "\t\t\t\tPRODUCT_NAME = \""
        + TARGET_NAME
        + "\";"
    )

    lines.append(
        "\t\t\t\tSWIFT_VERSION = 5.0;"
    )

    lines.append(
        "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";"
    )

    lines.append(
        "\t\t\t};"
    )

    lines.append(
        "\t\t\tname = Release;"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End XCBuildConfiguration section */"
    )

    lines.append("")

    # ========================================================
    # XCConfigurationList
    # ========================================================

    lines.append(
        "/* Begin XCConfigurationList section */"
    )

    lines.append(
        "\t\t"
        + data.project_config_list_id
        + " /* Build configuration list for PBXProject \""
        + PROJECT_NAME
        + "\" */ = {"
    )

    lines.append(
        "\t\t\tisa = XCConfigurationList;"
    )

    lines.append(
        "\t\t\tbuildConfigurations = ("
    )

    lines.append(
        "\t\t\t\t"
        + data.debug_project_config_id
        + " /* Debug */,"
    )

    lines.append(
        "\t\t\t\t"
        + data.release_project_config_id
        + " /* Release */,"
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\tdefaultConfigurationIsVisible = 0;"
    )

    lines.append(
        "\t\t\tdefaultConfigurationName = Release;"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "\t\t"
        + data.target_config_list_id
        + " /* Build configuration list for PBXNativeTarget \""
        + TARGET_NAME
        + "\" */ = {"
    )

    lines.append(
        "\t\t\tisa = XCConfigurationList;"
    )

    lines.append(
        "\t\t\tbuildConfigurations = ("
    )

    lines.append(
        "\t\t\t\t"
        + data.debug_target_config_id
        + " /* Debug */,"
    )

    lines.append(
        "\t\t\t\t"
        + data.release_target_config_id
        + " /* Release */,"
    )

    lines.append(
        "\t\t\t);"
    )

    lines.append(
        "\t\t\tdefaultConfigurationIsVisible = 0;"
    )

    lines.append(
        "\t\t\tdefaultConfigurationName = Release;"
    )

    lines.append(
        "\t\t};"
    )

    lines.append(
        "/* End XCConfigurationList section */"
    )

    lines.append("")

    # ========================================================
    # END
    # ========================================================

    lines.append(
        "\t};"
    )

    lines.append(
        "\trootObject = "
        + data.project_id
        + " /* Project object */;"
    )

    lines.append(
        "}"
    )

    return "\n".join(
        lines
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("")
    print("============================================")
    print(" Asasec Xcode Project Generator")
    print("============================================")
    print("")

    print(
        "Project : "
        + PROJECT_NAME
    )

    print(
        "Target  : "
        + TARGET_NAME
    )

    print(
        "Bundle  : "
        + BUNDLE_IDENTIFIER
    )

    print("")

    if not os.path.isdir(
        SOURCE_ROOT
    ):

        raise SystemExit(
            "HATA: "
            + SOURCE_ROOT
            + " klasörü bulunamadı."
        )

    # --------------------------------------------------------
    # Scan
    # --------------------------------------------------------

    files = scan_project_files()
    assets = scan_asset_catalogs()

    print(
        "Kaynak / resource dosyaları: "
        + str(len(files))
    )

    print(
        "Asset catalogları: "
        + str(len(assets))
    )

    print("")

    for path in files:

        print(
            "  FILE     "
            + path
        )

    for path in assets:

        print(
            "  ASSET    "
            + path
        )

    print("")

    # --------------------------------------------------------
    # Remove old project
    # --------------------------------------------------------

    if os.path.isdir(
        PROJECT_DIRECTORY
    ):

        print(
            "Eski xcodeproj siliniyor..."
        )

        shutil.rmtree(
            PROJECT_DIRECTORY
        )

    os.makedirs(
        PROJECT_DIRECTORY,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    print(
        "project.pbxproj oluşturuluyor..."
    )

    project_text = generate_project()

    with open(
        PROJECT_FILE,
        "w",
        encoding="utf-8",
        newline="\n"
    ) as file:

        file.write(
            project_text
        )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not os.path.isfile(
        PROJECT_FILE
    ):

        raise SystemExit(
            "HATA: project.pbxproj oluşturulamadı."
        )

    if os.path.getsize(
        PROJECT_FILE
    ) == 0:

        raise SystemExit(
            "HATA: project.pbxproj boş oluşturuldu."
        )

    print("")

    print(
        "project.pbxproj oluşturuldu:"
    )

    print(
        "  "
        + PROJECT_FILE
    )

    print("")

    print(
        "Dosya boyutu: "
        + str(
            os.path.getsize(
                PROJECT_FILE
            )
        )
        + " bytes"
    )

    print("")

    print(
        "Kaynak sayısı: "
        + str(len(files))
    )

    print(
        "Asset catalog sayısı: "
        + str(len(assets))
    )

    print("")

    print(
        "============================================"
    )

    print(
        " Xcode project hazır."
    )

    print(
        "============================================"
    )

    print("")


if __name__ == "__main__":

    main()
