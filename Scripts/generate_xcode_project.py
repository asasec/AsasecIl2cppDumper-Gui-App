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

    ".h": "sourcecode.c.h",
    ".hh": "sourcecode.cpp.h",
    ".hpp": "sourcecode.cpp.h",
}

RESOURCE_TYPES = {
    ".storyboard": "file.storyboard",
    ".xib": "file.xib",

    ".json": "text.json",
    ".strings": "text.plist.strings",
}

SPECIAL_DIRECTORIES = {
    ".xcassets": "folder.assetcatalog",
}


# ============================================================
# UUID
# ============================================================

def make_uuid(value):
    """
    Deterministic UUID.

    Aynı dosya aynı UUID'yi üretir.
    Böylece her GitHub Actions çalışmasında
    gereksiz UUID değişiklikleri oluşmaz.
    """

    return uuid.uuid5(
        uuid.NAMESPACE_URL,
        "asasec-xcode-project:" + value
    ).hex.upper()[:24]


# ============================================================
# HELPERS
# ============================================================

def quote(value):
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


def normalize(path):
    return path.replace(
        os.sep,
        "/"
    )


def extension(path):
    return os.path.splitext(
        path
    )[1].lower()


def is_source(path):
    return extension(path) in SOURCE_TYPES


def is_resource(path):
    return extension(path) in RESOURCE_TYPES


# ============================================================
# PROJECT SCANNER
# ============================================================

def scan_files():

    files = []

    if not os.path.isdir(SOURCE_ROOT):

        raise RuntimeError(
            "Kaynak klasörü bulunamadı: "
            + SOURCE_ROOT
        )

    for root, directories, filenames in os.walk(
        SOURCE_ROOT
    ):

        directories[:] = [
            directory
            for directory in directories
            if directory not in {
                ".git",
                "DerivedData",
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

            # Info.plist build resource değildir.
            if filename == "Info.plist":
                continue

            if (
                is_source(relative_path)
                or
                is_resource(relative_path)
            ):
                files.append(
                    relative_path
                )

    return sorted(files)


def scan_asset_catalogs():

    catalogs = []

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

                catalogs.append(
                    relative_path
                )

                directories.remove(
                    directory
                )

    return sorted(catalogs)


# ============================================================
# PBX DATA
# ============================================================

class PBXData:

    def __init__(self):

        self.file_references = []
        self.build_files = []

        self.groups = []

        self.source_build_files = []
        self.resource_build_files = []

        self.root_group_id = make_uuid(
            "group:root"
        )

        self.app_group_id = make_uuid(
            "group:" + APP_DIRECTORY
        )

        self.products_group_id = make_uuid(
            "group:products"
        )

        self.project_id = make_uuid(
            "project:" + PROJECT_NAME
        )

        self.target_id = make_uuid(
            "target:" + TARGET_NAME
        )

        self.sources_phase_id = make_uuid(
            "sources:" + TARGET_NAME
        )

        self.resources_phase_id = make_uuid(
            "resources:" + TARGET_NAME
        )

        self.frameworks_phase_id = make_uuid(
            "frameworks:" + TARGET_NAME
        )

        self.project_config_list_id = make_uuid(
            "project-config:" + PROJECT_NAME
        )

        self.target_config_list_id = make_uuid(
            "target-config:" + TARGET_NAME
        )

        self.debug_project_config_id = make_uuid(
            "project-debug:" + PROJECT_NAME
        )

        self.release_project_config_id = make_uuid(
            "project-release:" + PROJECT_NAME
        )

        self.debug_target_config_id = make_uuid(
            "target-debug:" + TARGET_NAME
        )

        self.release_target_config_id = make_uuid(
            "target-release:" + TARGET_NAME
        )


# ============================================================
# GROUP TREE
# ============================================================

class Group:

    def __init__(
        self,
        group_id,
        name,
        path,
        parent=None
    ):

        self.id = group_id
        self.name = name
        self.path = path
        self.parent = parent

        self.children = []


def create_group_tree(data):

    root = Group(
        data.root_group_id,
        None,
        None
    )

    app_group = Group(
        data.app_group_id,
        APP_DIRECTORY,
        APP_DIRECTORY,
        root
    )

    products_group = Group(
        data.products_group_id,
        "Products",
        None,
        root
    )

    root.children.append(
        app_group
    )

    root.children.append(
        products_group
    )

    group_map = {
        "": app_group
    }

    # Kaynak dosyalar
    all_files = scan_files()

    # Asset cataloglar
    asset_catalogs = scan_asset_catalogs()

    all_paths = []

    for path in all_files:
        all_paths.append(path)

    for path in asset_catalogs:
        all_paths.append(path)

    for relative_path in sorted(
        all_paths
    ):

        directory = os.path.dirname(
            relative_path
        )

        if directory == "":
            continue

        current = app_group
        current_path = ""

        for part in directory.split("/"):

            if current_path == "":
                current_path = part
            else:
                current_path += "/" + part

            if current_path not in group_map:

                group_id = make_uuid(
                    "group:" + current_path
                )

                new_group = Group(
                    group_id,
                    part,
                    part,
                    current
                )

                current.children.append(
                    new_group
                )

                group_map[
                    current_path
                ] = new_group

            current = group_map[
                current_path
            ]

    data.groups = root

    return root


# ============================================================
# PBX FILES
# ============================================================

def add_file(
    data,
    group_map,
    relative_path
):

    filename = os.path.basename(
        relative_path
    )

    file_id = make_uuid(
        "file:" + relative_path
    )

    build_id = make_uuid(
        "build:" + relative_path
    )

    file_type = SOURCE_TYPES.get(
        extension(relative_path)
    )

    if file_type is None:

        file_type = RESOURCE_TYPES.get(
            extension(relative_path)
        )

    if file_type is None:
        return

    data.file_references.append(
        (
            file_id,
            filename,
            file_type,
            relative_path
        )
    )

    data.build_files.append(
        (
            build_id,
            filename,
            file_id
        )
    )

    if is_source(relative_path):

        data.source_build_files.append(
            build_id
        )

    elif is_resource(relative_path):

        data.resource_build_files.append(
            build_id
        )

    directory = os.path.dirname(
        relative_path
    )

    group = group_map.get(
        directory
    )

    if group is None:
        group = group_map[""]

    group.children.append(
        (
            file_id,
            filename
        )
    )


def add_asset_catalog(
    data,
    group_map,
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
        (
            file_id,
            filename,
            "folder.assetcatalog",
            relative_path
        )
    )

    data.build_files.append(
        (
            build_id,
            filename,
            file_id
        )
    )

    data.resource_build_files.append(
        build_id
    )

    directory = os.path.dirname(
        relative_path
    )

    group = group_map.get(
        directory
    )

    if group is None:
        group = group_map[""]

    group.children.append(
        (
            file_id,
            filename
        )
    )


def collect_group_map(group):

    result = {
        ""
        if group.parent is None
        else group.path:
        group
    }

    for child in group.children:

        if isinstance(
            child,
            Group
        ):

            result.update(
                collect_group_map(
                    child
                )
            )

    return result


# ============================================================
# PBX GROUP GENERATOR
# ============================================================

def generate_groups(
    group,
    output
):

    output.append(
        "\t\t"
        + group.id
        + " = {"
    )

    output.append(
        "\t\t\tisa = PBXGroup;"
    )

    output.append(
        "\t\t\tchildren = ("
    )

    children = list(
        group.children
    )

    children.sort(
        key=lambda item:
        (
            0
            if isinstance(item, Group)
            else 1,
            (
                item.name
                if isinstance(item, Group)
                else item[1]
            ).lower()
        )
    )

    for child in children:

        if isinstance(
            child,
            Group
        ):

            comment = child.name

            output.append(
                "\t\t\t\t"
                + child.id
                + " /* "
                + comment
                + " */,"
            )

        else:

            file_id, filename = child

            output.append(
                "\t\t\t\t"
                + file_id
                + " /* "
                + filename
                + " */,"
            )

    output.append(
        "\t\t\t);"
    )

    if group.name is not None:

        output.append(
            "\t\t\tname = "
            + quote(group.name)
            + ";"
        )

        output.append(
            "\t\t\tpath = "
            + quote(group.path)
            + ";"
        )

    output.append(
        "\t\t\tsourceTree = \"<group>\";"
    )

    output.append(
        "\t\t};"
    )

    output.append("")

    for child in children:

        if isinstance(
            child,
            Group
        ):

            generate_groups(
                child,
                output
            )


# ============================================================
# PROJECT GENERATION
# ============================================================

def generate_project():

    data = PBXData()

    root = create_group_tree(
        data
    )

    group_map = collect_group_map(
        root
    )

    source_files = scan_files()

    for relative_path in source_files:

        add_file(
            data,
            group_map,
            relative_path
        )

    asset_catalogs = scan_asset_catalogs()

    for relative_path in asset_catalogs:

        add_asset_catalog(
            data,
            group_map,
            relative_path
        )

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    product_file_id = make_uuid(
        "product:" + TARGET_NAME
    )

    data.file_references.append(
        (
            product_file_id,
            TARGET_NAME + ".app",
            "wrapper.application",
            TARGET_NAME + ".app"
        )
    )

    products_group = None

    for child in root.children:

        if (
            isinstance(child, Group)
            and child.id == data.products_group_id
        ):

            products_group = child

            break

    if products_group is not None:

        products_group.children.append(
            (
                product_file_id,
                TARGET_NAME + ".app"
            )
        )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PBXBuildFile
    # --------------------------------------------------------

    lines.append(
        "/* Begin PBXBuildFile section */"
    )

    for (
        build_id,
        filename,
        file_id
    ) in data.build_files:

        lines.append(
            "\t\t"
            + build_id
            + " /* "
            + filename
            + " in "
            + (
                "Sources"
                if build_id in data.source_build_files
                else "Resources"
            )
            + " */ = {"
        )

        lines.append(
            "\t\t\tisa = PBXBuildFile;"
        )

        lines.append(
            "\t\t\tfileRef = "
            + file_id
            + " /* "
            + filename
            + " */;"
        )

        lines.append(
            "\t\t};"
        )

    lines.append(
        "/* End PBXBuildFile section */"
    )

    lines.append("")

    # --------------------------------------------------------
    # PBXFileReference
    # --------------------------------------------------------

    lines.append(
        "/* Begin PBXFileReference section */"
    )

    for (
        file_id,
        filename,
        file_type,
        path
    ) in data.file_references:

        lines.append(
            "\t\t"
            + file_id
            + " /* "
            + filename
            + " */ = {"
        )

        lines.append(
            "\t\t\tisa = PBXFileReference;"
        )

        if file_type == "wrapper.application":

            lines.append(
                "\t\t\texplicitFileType = wrapper.application;"
            )

            lines.append(
                "\t\t\tincludeInIndex = 0;"
            )

        else:

            lines.append(
                "\t\t\tlastKnownFileType = "
                + file_type
                + ";"
            )

        lines.append(
            "\t\t\tpath = "
            + quote(path)
            + ";"
        )

        if file_type == "wrapper.application":

            lines.append(
                "\t\t\tsourceTree = BUILT_PRODUCTS_DIR;"
            )

        else:

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

    # --------------------------------------------------------
    # Frameworks
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Groups
    # --------------------------------------------------------

    lines.append(
        "/* Begin PBXGroup section */"
    )

    group_output = []

    generate_groups(
        root,
        group_output
    )

    lines.extend(
        group_output
    )

    lines.append(
        "/* End PBXGroup section */"
    )

    lines.append("")

    # --------------------------------------------------------
    # Native Target
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PBXProject
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Resources
    # --------------------------------------------------------

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

        filename = ""

        for (
            candidate_id,
            candidate_filename,
            candidate_file_id
        ) in data.build_files:

            if candidate_id == build_id:

                filename = candidate_filename

                break

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

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

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

        filename = ""

        for (
            candidate_id,
            candidate_filename,
            candidate_file_id
        ) in data.build_files:

            if candidate_id == build_id:

                filename = candidate_filename

                break

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

    # --------------------------------------------------------
    # Build Configurations
    # --------------------------------------------------------

    lines.append(
        "/* Begin XCBuildConfiguration section */"
    )

    # Project Debug

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

    # Project Release

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

    # Target Debug

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

    # Target Release

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

    # --------------------------------------------------------
    # Configuration Lists
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # End
    # --------------------------------------------------------

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
        "Project : " + PROJECT_NAME
    )

    print(
        "Target  : " + TARGET_NAME
    )

    print(
        "Bundle  : " + BUNDLE_IDENTIFIER
    )

    print("")

    if not os.path.isdir(
        APP_DIRECTORY
    ):

        raise SystemExit(
            "HATA: "
            + APP_DIRECTORY
            + " klasörü bulunamadı."
        )

    # --------------------------------------------------------
    # Scan
    # --------------------------------------------------------

    files = scan_files()
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
    # Recreate xcodeproj
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
        "Toplam kaynak:"
        + " "
        + str(len(files))
    )

    print(
        "Toplam asset:"
        + " "
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
