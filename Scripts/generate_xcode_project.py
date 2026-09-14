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

# ------------------------------------------------------------
# IMPORTANT
#
# SOURCE_ROOT is the real filesystem root containing:
#
# App/
# Components/
# Controllers/
# Services/
# Theme/
# Info.plist
#
# Do NOT create another PBX group with path=APP_DIRECTORY
# underneath this root.
# ------------------------------------------------------------

SOURCE_ROOT = APP_DIRECTORY


# ============================================================
# HELPERS
# ============================================================

def normalize(path):
    path = path.replace("\\", "/")

    while "//" in path:
        path = path.replace("//", "/")

    if path == ".":
        return ""

    if path.startswith("./"):
        path = path[2:]

    return path.rstrip("/")


def make_uuid(seed):
    return uuid.uuid5(
        uuid.NAMESPACE_URL,
        "asasec-xcode-generator:" + seed
    ).hex[:24].upper()


def xcode_quote(value):
    return value.replace("\\", "\\\\").replace('"', '\\"')


# ============================================================
# DATA CLASSES
# ============================================================

class Group:
    def __init__(
        self,
        group_id,
        name,
        path=None,
        parent=None,
        is_root=False
    ):
        self.id = group_id
        self.name = name
        self.path = path
        self.parent = parent
        self.children = []
        self.files = []
        self.is_root = is_root


class ProjectData:
    def __init__(self):
        # ----------------------------------------------------
        # Main IDs
        # ----------------------------------------------------

        self.project_id = make_uuid("project")
        self.target_id = make_uuid("target")

        self.root_group_id = make_uuid("group:root")
        self.products_group_id = make_uuid("group:products")

        self.sources_phase_id = make_uuid("phase:sources")
        self.resources_phase_id = make_uuid("phase:resources")
        self.frameworks_phase_id = make_uuid("phase:frameworks")

        self.sources_build_file_id = make_uuid("build:sources")
        self.resources_build_file_id = make_uuid("build:resources")
        self.frameworks_build_file_id = make_uuid("build:frameworks")

        self.configuration_list_project_id = make_uuid(
            "configuration-list:project"
        )

        self.configuration_list_target_id = make_uuid(
            "configuration-list:target"
        )

        self.debug_project_config_id = make_uuid(
            "project-config:debug"
        )

        self.release_project_config_id = make_uuid(
            "project-config:release"
        )

        self.debug_target_config_id = make_uuid(
            "target-config:debug"
        )

        self.release_target_config_id = make_uuid(
            "target-config:release"
        )

        self.app_file_reference_id = make_uuid(
            "file:app-bundle"
        )

        self.info_plist_file_reference_id = make_uuid(
            "file:Info.plist"
        )

        self.info_plist_build_file_id = make_uuid(
            "build:Info.plist"
        )

        # ----------------------------------------------------
        # Group tree
        # ----------------------------------------------------

        self.root_group = None

        # IMPORTANT:
        #
        # "" -> actual SOURCE_ROOT
        #
        # We do NOT map "" to an extra App group.
        #
        self.group_map = {}

        # ----------------------------------------------------
        # File collections
        # ----------------------------------------------------

        self.file_references = {}
        self.build_files = {}

        self.source_build_files = []
        self.resource_build_files = []
        self.framework_build_files = []

        self.all_files = []


# ============================================================
# CREATE GROUP TREE
# ============================================================

def create_group_tree(data):

    # --------------------------------------------------------
    # ROOT PBX GROUP
    #
    # This group represents SOURCE_ROOT itself.
    #
    # Since the .xcodeproj sits next to SOURCE_ROOT, this
    # group must NOT point to APP_DIRECTORY again.
    #
    # Therefore:
    #
    #     name = PROJECT_NAME
    #     path = None
    #
    # Files are resolved relative to SOURCE_ROOT.
    # --------------------------------------------------------

    root = Group(
        data.root_group_id,
        name=PROJECT_NAME,
        path=None,
        parent=None,
        is_root=True
    )

    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    products_group = Group(
        data.products_group_id,
        name="Products",
        path=None,
        parent=root
    )

    root.children.append(products_group)

    # --------------------------------------------------------
    # ROOT GROUP MAPPING
    #
    # This is the critical fix.
    #
    # If relative_path is:
    #
    #     App/AppDelegate.swift
    #
    # ensure_group("App") creates:
    #
    #     ROOT
    #       └── App
    #            └── AppDelegate.swift
    #
    # NOT:
    #
    #     App
    #       └── App
    #            └── AppDelegate.swift
    # --------------------------------------------------------

    data.root_group = root
    data.group_map[""] = root

    return root


# ============================================================
# ENSURE GROUP
# ============================================================

def ensure_group(data, directory):

    directory = normalize(directory)

    if directory == "":
        return data.root_group

    if directory in data.group_map:
        return data.group_map[directory]

    parent_directory = normalize(
        os.path.dirname(directory)
    )

    parent_group = ensure_group(
        data,
        parent_directory
    )

    name = os.path.basename(directory)

    group_id = make_uuid(
        "group:" + directory
    )

    group = Group(
        group_id,
        name=name,
        path=name,
        parent=parent_group
    )

    parent_group.children.append(group)

    data.group_map[directory] = group

    return group


# ============================================================
# SCAN PROJECT FILES
# ============================================================

def scan_project_files():

    files = []

    if not os.path.isdir(SOURCE_ROOT):
        print(
            "ERROR: SOURCE_ROOT bulunamadı:",
            SOURCE_ROOT
        )
        return files

    ignored_directories = {
        ".git",
        ".github",
        "build",
        "DerivedData",
        ".build",
        "__pycache__"
    }

    ignored_files = {
        ".DS_Store"
    }

    for root, dirs, filenames in os.walk(
        SOURCE_ROOT
    ):

        # ----------------------------------------------------
        # Ignore directories
        # ----------------------------------------------------

        dirs[:] = [
            d
            for d in dirs
            if d not in ignored_directories
        ]

        for filename in filenames:

            if filename in ignored_files:
                continue

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

            # ------------------------------------------------
            # Never add the generated pbxproj itself
            # ------------------------------------------------

            if relative_path.startswith(
                PROJECT_DIRECTORY + "/"
            ):
                continue

            # ------------------------------------------------
            # Info.plist is handled separately.
            # ------------------------------------------------

            if relative_path == "Info.plist":
                continue

            # ------------------------------------------------
            # Asset catalogs are resources but their contents
            # should NOT be added individually.
            # ------------------------------------------------

            if ".xcassets/" in relative_path:
                continue

            # ------------------------------------------------
            # Ignore hidden files
            # ------------------------------------------------

            if filename.startswith("."):
                continue

            files.append({
                "full_path": full_path,
                "relative_path": relative_path,
                "filename": filename
            })

    files.sort(
        key=lambda item: item["relative_path"].lower()
    )

    return files


# ============================================================
# SCAN ASSET CATALOGS
# ============================================================

def scan_asset_catalogs():

    assets = []

    if not os.path.isdir(SOURCE_ROOT):
        return assets

    for root, dirs, filenames in os.walk(
        SOURCE_ROOT
    ):

        dirs[:] = [
            d
            for d in dirs
            if d not in {
                ".git",
                ".github",
                "build",
                "DerivedData",
                ".build",
                "__pycache__"
            }
        ]

        for directory in list(dirs):

            if directory.endswith(".xcassets"):

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

                assets.append({
                    "full_path": full_path,
                    "relative_path": relative_path,
                    "filename": directory
                })

                # Do not descend into xcassets.
                dirs.remove(directory)

    assets.sort(
        key=lambda item: item["relative_path"].lower()
    )

    return assets


# ============================================================
# FILE TYPE
# ============================================================

def is_source_file(path):

    extension = os.path.splitext(
        path
    )[1].lower()

    return extension in {
        ".swift",
        ".m",
        ".mm",
        ".c",
        ".cc",
        ".cpp",
        ".cxx",
        ".h",
        ".hpp"
    }


def is_resource_file(path):

    extension = os.path.splitext(
        path
    )[1].lower()

    return extension in {
        ".storyboard",
        ".xib",
        ".json",
        ".strings",
        ".plist",
        ".xcconfig",
        ".metal",
        ".mlmodel",
        ".txt",
        ".html",
        ".css",
        ".js",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".heic",
        ".pdf"
    }


# ============================================================
# ADD FILE
# ============================================================

def add_file(data, item):

    relative_path = normalize(
        item["relative_path"]
    )

    if not relative_path:
        return

    # --------------------------------------------------------
    # Group path
    #
    # Example:
    #
    # App/AppDelegate.swift
    #
    # dirname =>
    #
    # App
    #
    # ensure_group("App")
    # --------------------------------------------------------

    group_path = normalize(
        os.path.dirname(relative_path)
    )

    group = ensure_group(
        data,
        group_path
    )

    file_id = make_uuid(
        "file:" + relative_path
    )

    file_reference = {
        "id": file_id,
        "path": relative_path,
        "name": item["filename"],
        "group": group.id
    }

    data.file_references[
        relative_path
    ] = file_reference

    data.all_files.append(
        file_reference
    )

    group.files.append(
        file_reference
    )

    # --------------------------------------------------------
    # Determine build phase
    # --------------------------------------------------------

    if is_source_file(relative_path):

        build_id = make_uuid(
            "build:" + relative_path
        )

        build_file = {
            "id": build_id,
            "file_ref": file_id,
            "path": relative_path
        }

        data.build_files[
            relative_path
        ] = build_file

        data.source_build_files.append(
            build_file
        )

    elif is_resource_file(relative_path):

        build_id = make_uuid(
            "build:" + relative_path
        )

        build_file = {
            "id": build_id,
            "file_ref": file_id,
            "path": relative_path
        }

        data.build_files[
            relative_path
        ] = build_file

        data.resource_build_files.append(
            build_file
        )


# ============================================================
# ADD ASSET CATALOG
# ============================================================

def add_asset_catalog(data, item):

    relative_path = normalize(
        item["relative_path"]
    )

    group_path = normalize(
        os.path.dirname(relative_path)
    )

    group = ensure_group(
        data,
        group_path
    )

    file_id = make_uuid(
        "file:" + relative_path
    )

    file_reference = {
        "id": file_id,
        "path": relative_path,
        "name": item["filename"],
        "group": group.id,
        "asset_catalog": True
    }

    data.file_references[
        relative_path
    ] = file_reference

    data.all_files.append(
        file_reference
    )

    group.files.append(
        file_reference
    )

    build_id = make_uuid(
        "build:" + relative_path
    )

    build_file = {
        "id": build_id,
        "file_ref": file_id,
        "path": relative_path
    }

    data.build_files[
        relative_path
    ] = build_file

    data.resource_build_files.append(
        build_file
    )


# ============================================================
# STRING HELPERS
# ============================================================

def indent(level):
    return "    " * level


def emit_file_reference(
    lines,
    file_ref,
    level=2
):

    file_id = file_ref["id"]
    name = file_ref["name"]
    path = file_ref["path"]

    lines.append(
        "{}{} /* {} */ = {{isa = PBXFileReference; "
        "fileEncoding = 4; lastKnownFileType = {}; "
        "path = \"{}\"; sourceTree = \"<group>\"; }};"
        .format(
            indent(level),
            file_id,
            name,
            file_type_for_path(path),
            xcode_quote(path)
        )
    )


def file_type_for_path(path):

    lower = path.lower()

    if lower.endswith(".swift"):
        return "sourcecode.swift"

    if lower.endswith(".m"):
        return "sourcecode.c.objc"

    if lower.endswith(".mm"):
        return "sourcecode.cpp.objcpp"

    if lower.endswith(".c"):
        return "sourcecode.c.c"

    if lower.endswith(".cc"):
        return "sourcecode.cpp.cpp"

    if lower.endswith(".cpp"):
        return "sourcecode.cpp.cpp"

    if lower.endswith(".cxx"):
        return "sourcecode.cpp.cpp"

    if lower.endswith(".h"):
        return "sourcecode.c.h"

    if lower.endswith(".hpp"):
        return "sourcecode.cpp.h"

    if lower.endswith(".storyboard"):
        return "file.storyboard"

    if lower.endswith(".xib"):
        return "file.xib"

    if lower.endswith(".json"):
        return "text.json"

    if lower.endswith(".strings"):
        return "text.plist.strings"

    if lower.endswith(".plist"):
        return "text.plist.xml"

    if lower.endswith(".xcassets"):
        return "folder.assetcatalog"

    if lower.endswith(".metal"):
        return "sourcecode.metal"

    if lower.endswith(".png"):
        return "image.png"

    if lower.endswith(".jpg"):
        return "image.jpeg"

    if lower.endswith(".jpeg"):
        return "image.jpeg"

    if lower.endswith(".gif"):
        return "image.gif"

    if lower.endswith(".pdf"):
        return "image.pdf"

    if lower.endswith(".txt"):
        return "text"

    return "text"


# ============================================================
# EMIT GROUP
# ============================================================

def emit_group(
    lines,
    group,
    level=2
):

    if group.is_root:

        children = []

        for child in group.children:
            children.append(
                "{} /* {} */".format(
                    child.id,
                    child.name
                )
            )

        # Root files
        for file_ref in group.files:
            children.append(
                "{} /* {} */".format(
                    file_ref["id"],
                    file_ref["name"]
                )
            )

        lines.append(
            "{}{} /* {} */ = {{isa = PBXGroup; "
            "children = (\n"
            .format(
                indent(level),
                group.id,
                group.name
            )
        )

        for child in children:
            lines.append(
                "{}{},\n".format(
                    indent(level + 1),
                    child
                )
            )

        lines.append(
            "{}); "
            "name = \"{}\"; "
            "sourceTree = \"<group>\"; }};"
            "\n".format(
                indent(level),
                xcode_quote(group.name)
            )
        )

    else:

        children = []

        for child in group.children:
            children.append(
                "{} /* {} */".format(
                    child.id,
                    child.name
                )
            )

        for file_ref in group.files:
            children.append(
                "{} /* {} */".format(
                    file_ref["id"],
                    file_ref["name"]
                )
            )

        lines.append(
            "{}{} /* {} */ = {{isa = PBXGroup; "
            "children = (\n"
            .format(
                indent(level),
                group.id,
                group.name
            )
        )

        for child in children:
            lines.append(
                "{}{},\n".format(
                    indent(level + 1),
                    child
                )
            )

        lines.append(
            "{}); "
            "name = \"{}\"; "
            "path = \"{}\"; "
            "sourceTree = \"<group>\"; }};"
            "\n".format(
                indent(level),
                xcode_quote(group.name),
                xcode_quote(group.path or "")
            )
        )

    # --------------------------------------------------------
    # Recursively emit child groups
    # --------------------------------------------------------

    for child in group.children:

        if child.name == "Products":
            continue

        emit_group(
            lines,
            child,
            level
        )


# ============================================================
# PBX BUILD FILE
# ============================================================

def emit_build_file(
    lines,
    build_file,
    file_reference
):

    lines.append(
        "\t\t{} /* {} in Sources */ = "
        "{{isa = PBXBuildFile; fileRef = {} /* {} */; }};"
        .format(
            build_file["id"],
            file_reference["name"],
            file_reference["id"],
            file_reference["name"]
        )
    )


# ============================================================
# BUILD PHASE
# ============================================================

def emit_build_phase(
    lines,
    phase_id,
    name,
    build_files
):

    lines.append(
        "\t\t{} /* {} */ = {{isa = PBXSourcesBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n"
        .format(
            phase_id,
            name
        )
    )

    for build_file in build_files:

        file_ref = data_global.file_references[
            build_file["path"]
        ]

        lines.append(
            "\t\t\t{} /* {} in {} */,\n".format(
                build_file["id"],
                file_ref["name"],
                name
            )
        )

    lines.append(
        "\t\t); "
        "runOnlyForDeploymentPostprocessing = 0; "
        "};\n"
    )


# ============================================================
# CONFIGURATION
# ============================================================

def emit_configuration_lists(lines, data):

    lines.append(
        "\t\t{} /* Build configuration list for PBXProject \"{}\" */ = {{"
        "isa = XCConfigurationList; "
        "buildConfigurations = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "defaultConfigurationIsVisible = 0; "
        "defaultConfigurationName = Release; "
        "}};"
        .format(
            data.configuration_list_project_id,
            PROJECT_NAME,
            data.debug_project_config_id,
            data.release_project_config_id
        )
    )

    lines.append("")

    lines.append(
        "\t\t{} /* Build configuration list for PBXNativeTarget \"{}\" */ = {{"
        "isa = XCConfigurationList; "
        "buildConfigurations = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "defaultConfigurationIsVisible = 0; "
        "defaultConfigurationName = Release; "
        "}};"
        .format(
            data.configuration_list_target_id,
            TARGET_NAME,
            data.debug_target_config_id,
            data.release_target_config_id
        )
    )


# ============================================================
# GENERATE PROJECT
# ============================================================

def generate_project(data):

    lines = []

    lines.append("// !$*UTF8*$!")
    lines.append("{")
    lines.append("\tarchiveVersion = 1;")
    lines.append("\tclasses = {")
    lines.append("\t};")
    lines.append("\tobjectVersion = 56;")
    lines.append("\tobjects = {")

    # ========================================================
    # PBX BUILD FILES
    # ========================================================

    for relative_path, build_file in data.build_files.items():

        file_ref = data.file_references[
            relative_path
        ]

        phase_name = (
            "Resources"
            if build_file in data.resource_build_files
            else "Sources"
        )

        lines.append(
            "\t\t{} /* {} in {} */ = "
            "{{isa = PBXBuildFile; fileRef = {} /* {} */; }};"
            .format(
                build_file["id"],
                file_ref["name"],
                phase_name,
                file_ref["id"],
                file_ref["name"]
            )
        )

    # ========================================================
    # INFO.PLIST BUILD FILE
    # ========================================================

    lines.append(
        "\t\t{} /* Info.plist in Resources */ = "
        "{{isa = PBXBuildFile; fileRef = {} /* Info.plist */; }};"
        .format(
            data.info_plist_build_file_id,
            data.info_plist_file_reference_id
        )
    )

    # ========================================================
    # PBX FILE REFERENCES
    # ========================================================

    for relative_path, file_ref in data.file_references.items():

        lines.append(
            "\t\t{} /* {} */ = {{isa = PBXFileReference; "
            "fileEncoding = 4; lastKnownFileType = {}; "
            "path = \"{}\"; sourceTree = \"<group>\"; }};"
            .format(
                file_ref["id"],
                file_ref["name"],
                file_type_for_path(
                    relative_path
                ),
                xcode_quote(relative_path)
            )
        )

    # --------------------------------------------------------
    # Info.plist
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* Info.plist */ = "
        "{{isa = PBXFileReference; "
        "fileEncoding = 4; "
        "lastKnownFileType = text.plist.xml; "
        "path = \"Info.plist\"; "
        "sourceTree = \"<group>\"; }};"
        .format(
            data.info_plist_file_reference_id
        )
    )

    # --------------------------------------------------------
    # Product
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* {}.app */ = "
        "{{isa = PBXFileReference; "
        "explicitFileType = wrapper.application; "
        "includeInIndex = 0; "
        "path = \"{}.app\"; "
        "sourceTree = BUILT_PRODUCTS_DIR; }};"
        .format(
            data.app_file_reference_id,
            TARGET_NAME,
            TARGET_NAME
        )
    )

    # ========================================================
    # PBX GROUPS
    # ========================================================

    emit_group(
        lines,
        data.root_group,
        level=2
    )

    # --------------------------------------------------------
    # Products group
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* Products */ = {{isa = PBXGroup; "
        "children = (\n"
        "\t\t\t{} /* {}.app */,\n"
        "\t\t); "
        "name = Products; "
        "sourceTree = \"<group>\"; }};"
        .format(
            data.products_group_id,
            data.app_file_reference_id,
            TARGET_NAME
        )
    )

    # ========================================================
    # PBX NATIVE TARGET
    # ========================================================

    lines.append(
        "\t\t{} /* {} */ = {{isa = PBXNativeTarget; "
        "buildConfigurationList = {}; "
        "buildPhases = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "buildRules = (); "
        "dependencies = (); "
        "name = \"{}\"; "
        "productName = \"{}\"; "
        "productReference = {} /* {}.app */; "
        "productType = \"com.apple.product-type.application\"; "
        "}};"
        .format(
            data.target_id,
            TARGET_NAME,
            data.configuration_list_target_id,
            data.sources_phase_id,
            data.frameworks_phase_id,
            data.resources_phase_id,
            TARGET_NAME,
            TARGET_NAME,
            data.app_file_reference_id,
            TARGET_NAME
        )
    )

    # ========================================================
    # PBX PROJECT
    # ========================================================

    lines.append(
        "\t\t{} /* Project object */ = {{isa = PBXProject; "
        "attributes = {{\n"
        "\t\t\tLastUpgradeCheck = 1600;\n"
        "\t\t\tTargetAttributes = {{\n"
        "\t\t\t\t{} = {{\n"
        "\t\t\t\t\tCreatedOnToolsVersion = 16.0;\n"
        "\t\t\t\t}};\n"
        "\t\t\t}};\n"
        "\t\t}}; "
        "buildConfigurationList = {}; "
        "compatibilityVersion = \"Xcode 14.0\"; "
        "developmentRegion = en; "
        "hasScannedForEncodings = 0; "
        "knownRegions = (\n"
        "\t\t\ten,\n"
        "\t\t\tBase,\n"
        "\t\t); "
        "mainGroup = {} /* {} */; "
        "productRefGroup = {} /* Products */; "
        "projectDirPath = \"\"; "
        "projectRoot = \"\"; "
        "targets = (\n"
        "\t\t\t{},\n"
        "\t\t); "
        "}};"
        .format(
            data.project_id,
            data.target_id,
            data.configuration_list_project_id,
            data.root_group_id,
            PROJECT_NAME,
            data.products_group_id,
            data.target_id
        )
    )

    # ========================================================
    # BUILD PHASES
    # ========================================================

    # Sources
    lines.append(
        "\t\t{} /* Sources */ = {{isa = PBXSourcesBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n"
        .format(
            data.sources_phase_id
        )
    )

    for build_file in data.source_build_files:

        file_ref = data.file_references[
            build_file["path"]
        ]

        lines.append(
            "\t\t\t{} /* {} in Sources */,\n".format(
                build_file["id"],
                file_ref["name"]
            )
        )

    lines.append(
        "\t\t); "
        "runOnlyForDeploymentPostprocessing = 0; "
        "}};"
    )

    # Frameworks
    lines.append(
        "\t\t{} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n"
        .format(
            data.frameworks_phase_id
        )
    )

    for build_file in data.framework_build_files:

        file_ref = data.file_references[
            build_file["path"]
        ]

        lines.append(
            "\t\t\t{} /* {} in Frameworks */,\n".format(
                build_file["id"],
                file_ref["name"]
            )
        )

    lines.append(
        "\t\t); "
        "runOnlyForDeploymentPostprocessing = 0; "
        "}};"
    )

    # Resources
    lines.append(
        "\t\t{} /* Resources */ = {{isa = PBXResourcesBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n"
        .format(
            data.resources_phase_id
        )
    )

    for build_file in data.resource_build_files:

        file_ref = data.file_references[
            build_file["path"]
        ]

        lines.append(
            "\t\t\t{} /* {} in Resources */,\n".format(
                build_file["id"],
                file_ref["name"]
            )
        )

    # Info.plist
    lines.append(
        "\t\t\t{} /* Info.plist in Resources */,\n"
        .format(
            data.info_plist_build_file_id
        )
    )

    lines.append(
        "\t\t); "
        "runOnlyForDeploymentPostprocessing = 0; "
        "}};"
    )

    # ========================================================
    # CONFIGURATIONS
    # ========================================================

    # --------------------------------------------------------
    # PROJECT DEBUG
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* Debug */ = {{isa = XCBuildConfiguration; "
        "buildSettings = {{\n"
        "\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;\n"
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;\n"
        "\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;\n"
        "\t\t\t\tCOPY_PHASE_STRIP = NO;\n"
        "\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;\n"
        "\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;\n"
        "\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;\n"
        "\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;\n"
        "\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;\n"
        "\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;\n"
        "\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;\n"
        "\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;\n"
        "\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;\n"
        "\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;\n"
        "\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;\n"
        "\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;\n"
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;\n"
        "\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;\n"
        "\t\t\t\tONLY_ACTIVE_ARCH = YES;\n"
        "\t\t\t\tSDKROOT = iphoneos;\n"
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-Onone\";\n"
        "\t\t\t}}; "
        "name = Debug; "
        "}};"
        .format(
            data.debug_project_config_id
        )
    )

    # --------------------------------------------------------
    # PROJECT RELEASE
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* Release */ = {{isa = XCBuildConfiguration; "
        "buildSettings = {{\n"
        "\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;\n"
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;\n"
        "\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;\n"
        "\t\t\t\tCOPY_PHASE_STRIP = NO;\n"
        "\t\t\t\tDEBUG_INFORMATION_FORMAT = \"dwarf-with-dsym\";\n"
        "\t\t\t\tENABLE_NS_ASSERTIONS = NO;\n"
        "\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;\n"
        "\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;\n"
        "\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;\n"
        "\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;\n"
        "\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;\n"
        "\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;\n"
        "\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;\n"
        "\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;\n"
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;\n"
        "\t\t\t\tSDKROOT = iphoneos;\n"
        "\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = \"-O\";\n"
        "\t\t\t}}; "
        "name = Release; "
        "}};"
        .format(
            data.release_project_config_id
        )
    )

    # --------------------------------------------------------
    # TARGET DEBUG
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* Debug */ = {{isa = XCBuildConfiguration; "
        "buildSettings = {{\n"
        "\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;\n"
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;\n"
        "\t\t\t\tCODE_SIGN_STYLE = Automatic;\n"
        "\t\t\t\tCURRENT_PROJECT_VERSION = 1;\n"
        "\t\t\t\tDEVELOPMENT_TEAM = \"\";\n"
        "\t\t\t\tGENERATE_INFOPLIST_FILE = NO;\n"
        "\t\t\t\tINFOPLIST_FILE = \"{}/Info.plist\";\n"
        "\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = \"{}\";\n"
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;\n"
        "\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\n"
        "\t\t\t\t\t\"$(inherited)\",\n"
        "\t\t\t\t\t\"@executable_path/Frameworks\",\n"
        "\t\t\t\t);\n"
        "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {};\n"
        "\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";\n"
        "\t\t\t\tSWIFT_VERSION = 5.0;\n"
        "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";\n"
        "\t\t\t}}; "
        "name = Debug; "
        "}};"
        .format(
            APP_DIRECTORY,
            TARGET_NAME,
            BUNDLE_IDENTIFIER
        )
    )

    # --------------------------------------------------------
    # TARGET RELEASE
    # --------------------------------------------------------

    lines.append(
        "\t\t{} /* Release */ = {{isa = XCBuildConfiguration; "
        "buildSettings = {{\n"
        "\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;\n"
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;\n"
        "\t\t\t\tCODE_SIGN_STYLE = Automatic;\n"
        "\t\t\t\tCURRENT_PROJECT_VERSION = 1;\n"
        "\t\t\t\tDEVELOPMENT_TEAM = \"\";\n"
        "\t\t\t\tGENERATE_INFOPLIST_FILE = NO;\n"
        "\t\t\t\tINFOPLIST_FILE = \"{}/Info.plist\";\n"
        "\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = \"{}\";\n"
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;\n"
        "\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (\n"
        "\t\t\t\t\t\"$(inherited)\",\n"
        "\t\t\t\t\t\"@executable_path/Frameworks\",\n"
        "\t\t\t\t);\n"
        "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = {};\n"
        "\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";\n"
        "\t\t\t\tSWIFT_VERSION = 5.0;\n"
        "\t\t\t\tTARGETED_DEVICE_FAMILY = \"1,2\";\n"
        "\t\t\t}}; "
        "name = Release; "
        "}};"
        .format(
            APP_DIRECTORY,
            TARGET_NAME,
            BUNDLE_IDENTIFIER
        )
    )

    # ========================================================
    # CONFIGURATION LISTS
    # ========================================================

    lines.append(
        "\t\t{} /* Project configuration list */ = "
        "{{isa = XCConfigurationList; "
        "buildConfigurations = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "defaultConfigurationIsVisible = 0; "
        "defaultConfigurationName = Release; "
        "}};"
        .format(
            data.configuration_list_project_id,
            data.debug_project_config_id,
            data.release_project_config_id
        )
    )

    lines.append(
        "\t\t{} /* Target configuration list */ = "
        "{{isa = XCConfigurationList; "
        "buildConfigurations = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "defaultConfigurationIsVisible = 0; "
        "defaultConfigurationName = Release; "
        "}};"
        .format(
            data.configuration_list_target_id,
            data.debug_target_config_id,
            data.release_target_config_id
        )
    )

    # ========================================================
    # END OBJECTS
    # ========================================================

    lines.append("\t};")
    lines.append("\trootObject = {} /* Project object */;".format(
        data.project_id
    ))
    lines.append("}")

    # --------------------------------------------------------
    # Write file
    # --------------------------------------------------------

    os.makedirs(
        PROJECT_DIRECTORY,
        exist_ok=True
    )

    with open(
        PROJECT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(lines)
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("============================================")
    print(" Asasec Xcode Project Generator")
    print("============================================")
    print("Project :", PROJECT_NAME)
    print("Target  :", TARGET_NAME)
    print("Bundle  :", BUNDLE_IDENTIFIER)
    print("Source  :", SOURCE_ROOT)
    print()

    # --------------------------------------------------------
    # Check source root
    # --------------------------------------------------------

    if not os.path.isdir(SOURCE_ROOT):

        print(
            "ERROR: Kaynak klasörü bulunamadı:"
        )
        print(
            os.path.abspath(SOURCE_ROOT)
        )

        return 1

    # --------------------------------------------------------
    # Clean old generated project
    # --------------------------------------------------------

    if os.path.isdir(
        PROJECT_DIRECTORY
    ):

        print(
            "Eski Xcode projesi siliniyor..."
        )

        shutil.rmtree(
            PROJECT_DIRECTORY
        )

    # --------------------------------------------------------
    # Create data
    # --------------------------------------------------------

    data = ProjectData()

    # --------------------------------------------------------
    # Create PBX groups
    # --------------------------------------------------------

    create_group_tree(
        data
    )

    # --------------------------------------------------------
    # Scan normal files
    # --------------------------------------------------------

    project_files = scan_project_files()

    print(
        "Kaynak / resource dosyaları:",
        len(project_files)
    )

    for item in project_files:

        print(
            "  FILE",
            item["relative_path"]
        )

        add_file(
            data,
            item
        )

    # --------------------------------------------------------
    # Scan assets
    # --------------------------------------------------------

    asset_catalogs = scan_asset_catalogs()

    print(
        "Asset catalogları:",
        len(asset_catalogs)
    )

    for item in asset_catalogs:

        print(
            "  ASSET",
            item["relative_path"]
        )

        add_asset_catalog(
            data,
            item
        )

    # --------------------------------------------------------
    # Generate project
    # --------------------------------------------------------

    print()
    print(
        "Xcode project oluşturuluyor..."
    )

    generate_project(
        data
    )

    # --------------------------------------------------------
    # Final information
    # --------------------------------------------------------

    print()
    print("============================================")
    print(" Tamamlandı")
    print("============================================")
    print(
        "Project:",
        os.path.abspath(PROJECT_DIRECTORY)
    )

    print()
    print("Kontrol edilen dosya yolları:")

    for relative_path in sorted(
        data.file_references.keys()
    ):

        print(
            "  ✓",
            relative_path
        )

    print()
    print(
        "Build kaynakları:",
        len(data.source_build_files)
    )

    print(
        "Resources:",
        len(data.resource_build_files)
    )

    print()
    print(
        "ÖNEMLİ: Eski .xcodeproj tamamen silinip"
    )
    print(
        "yeni proje oluşturuldu."
    )

    return 0


# ============================================================
# GLOBAL BUILD PHASE HELPER
# ============================================================

data_global = None


if __name__ == "__main__":

    # --------------------------------------------------------
    # generate_project() build phase helper'larının data'ya
    # erişebilmesi için global referans.
    # --------------------------------------------------------

    original_generate_project = generate_project

    def generate_project_with_global(data):
        global data_global
        data_global = data
        return original_generate_project(data)

    generate_project = generate_project_with_global

    raise SystemExit(
        main()
    )
