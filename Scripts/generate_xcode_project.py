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
# REAL FILESYSTEM
#
# AsasecIl2cppDumper-Gui-App/
#
# ├── App/
# │   ├── AppDelegate.swift
# │   └── SceneDelegate.swift
# │
# ├── Components/
# │   ├── ModernCardView.swift
# │   ├── OutputConsoleView.swift
# │   └── PathInputView.swift
# │
# ├── Controllers/
# │   ├── MainViewController.swift
# │   └── SettingsViewController.swift
# │
# ├── Services/
# │   ├── DumpManager.swift
# │   └── FilePickerService.swift
# │
# ├── Theme/
# │   └── AppTheme.swift
# │
# ├── Assets.xcassets
# ├── LaunchScreen.storyboard
# └── Info.plist
#
# SOURCE_ROOT = gerçek kaynak klasörü.
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

    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )


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
        # MAIN IDS
        # ----------------------------------------------------

        self.project_id = make_uuid(
            "project"
        )

        self.target_id = make_uuid(
            "target"
        )

        self.root_group_id = make_uuid(
            "group:root"
        )

        self.products_group_id = make_uuid(
            "group:products"
        )

        # ----------------------------------------------------
        # BUILD PHASES
        # ----------------------------------------------------

        self.sources_phase_id = make_uuid(
            "phase:sources"
        )

        self.resources_phase_id = make_uuid(
            "phase:resources"
        )

        self.frameworks_phase_id = make_uuid(
            "phase:frameworks"
        )

        # ----------------------------------------------------
        # CONFIGURATION LISTS
        # ----------------------------------------------------

        self.configuration_list_project_id = make_uuid(
            "configuration-list:project"
        )

        self.configuration_list_target_id = make_uuid(
            "configuration-list:target"
        )

        # ----------------------------------------------------
        # PROJECT CONFIGURATIONS
        # ----------------------------------------------------

        self.debug_project_config_id = make_uuid(
            "project-config:debug"
        )

        self.release_project_config_id = make_uuid(
            "project-config:release"
        )

        # ----------------------------------------------------
        # TARGET CONFIGURATIONS
        # ----------------------------------------------------

        self.debug_target_config_id = make_uuid(
            "target-config:debug"
        )

        self.release_target_config_id = make_uuid(
            "target-config:release"
        )

        # ----------------------------------------------------
        # PRODUCT
        # ----------------------------------------------------

        self.app_file_reference_id = make_uuid(
            "file:app-bundle"
        )

        # ----------------------------------------------------
        # INFO.PLIST
        # ----------------------------------------------------

        self.info_plist_file_reference_id = make_uuid(
            "file:Info.plist"
        )

        # ----------------------------------------------------
        # GROUPS
        # ----------------------------------------------------

        self.root_group = None

        # IMPORTANT:
        #
        # "" = SOURCE_ROOT
        #
        # Burada ekstra "App" grubu oluşturulmaz.
        # ----------------------------------------------------

        self.group_map = {}

        # ----------------------------------------------------
        # FILES
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
    # ROOT
    #
    # Root group SOURCE_ROOT'u temsil eder.
    #
    # Dolayısıyla:
    #
    # path = None
    #
    # olmalıdır.
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

    root.children.append(
        products_group
    )

    # --------------------------------------------------------
    # ROOT MAPPING
    # --------------------------------------------------------

    data.root_group = root

    data.group_map[""] = root

    return root


# ============================================================
# ENSURE GROUP
# ============================================================

def ensure_group(data, directory):

    directory = normalize(
        directory
    )

    # --------------------------------------------------------
    # ROOT
    # --------------------------------------------------------

    if directory == "":
        return data.root_group

    # --------------------------------------------------------
    # EXISTING GROUP
    # --------------------------------------------------------

    if directory in data.group_map:
        return data.group_map[directory]

    # --------------------------------------------------------
    # PARENT
    # --------------------------------------------------------

    parent_directory = normalize(
        os.path.dirname(directory)
    )

    parent_group = ensure_group(
        data,
        parent_directory
    )

    # --------------------------------------------------------
    # CURRENT GROUP
    # --------------------------------------------------------

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

    data.group_map[directory] = group

    return group


# ============================================================
# REQUIRED FILE CHECK
# ============================================================

def validate_required_files():

    print()
    print("============================================")
    print(" ZORUNLU DOSYA KONTROLÜ")
    print("============================================")

    required_files = [
        "Info.plist",
        "LaunchScreen.storyboard"
    ]

    missing = 0

    for relative_path in required_files:

        full_path = os.path.join(
            SOURCE_ROOT,
            relative_path
        )

        if os.path.isfile(full_path):

            print(
                "  ✓",
                relative_path
            )

        else:

            print(
                "  ✗ MISSING:",
                relative_path
            )

            print(
                "    Beklenen:",
                os.path.abspath(full_path)
            )

            missing += 1

    print()

    if missing > 0:

        print(
            "ERROR:",
            missing,
            "zorunlu dosya bulunamadı."
        )

        return False

    print(
        "Tüm zorunlu dosyalar mevcut."
    )

    return True


# ============================================================
# LAUNCHSCREEN CHECK
# ============================================================

def validate_launch_screen_file():

    launch_screen = os.path.join(
        SOURCE_ROOT,
        "LaunchScreen.storyboard"
    )

    if not os.path.isfile(
        launch_screen
    ):

        return False

    if os.path.getsize(
        launch_screen
    ) == 0:

        print(
            "ERROR: LaunchScreen.storyboard boş."
        )

        print(
            os.path.abspath(
                launch_screen
            )
        )

        return False

    return True


# ============================================================
# INFO PLIST CHECK
# ============================================================

def validate_info_plist_file():

    info_plist = os.path.join(
        SOURCE_ROOT,
        "Info.plist"
    )

    if not os.path.isfile(
        info_plist
    ):

        return False

    if os.path.getsize(
        info_plist
    ) == 0:

        print(
            "ERROR: Info.plist boş."
        )

        print(
            os.path.abspath(
                info_plist
            )
        )

        return False

    return True


# ============================================================
# SCAN PROJECT FILES
# ============================================================

def scan_project_files():

    files = []

    if not os.path.isdir(
        SOURCE_ROOT
    ):

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
        "__pycache__",
        ".xcodeproj"
    }

    ignored_files = {
        ".DS_Store"
    }

    for root, dirs, filenames in os.walk(
        SOURCE_ROOT
    ):

        # ----------------------------------------------------
        # IGNORE DIRECTORIES
        # ----------------------------------------------------

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in ignored_directories
        ]

        for filename in filenames:

            if filename in ignored_files:
                continue

            if filename.startswith("."):
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

            if not relative_path:
                continue

            # ------------------------------------------------
            # Info.plist ayrı tutuluyor.
            # ------------------------------------------------

            if relative_path == "Info.plist":
                continue

            # ------------------------------------------------
            # Generated Xcode project.
            # ------------------------------------------------

            if relative_path.endswith(
                ".xcodeproj/project.pbxproj"
            ):
                continue

            # ------------------------------------------------
            # Asset catalog contents.
            #
            # Assets.xcassets tek dosya/reference olarak
            # ayrıca ekleniyor.
            # ------------------------------------------------

            if ".xcassets/" in relative_path:
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

    if not os.path.isdir(
        SOURCE_ROOT
    ):

        return assets

    ignored_directories = {
        ".git",
        ".github",
        "build",
        "DerivedData",
        ".build",
        "__pycache__",
        ".xcodeproj"
    }

    for root, dirs, filenames in os.walk(
        SOURCE_ROOT
    ):

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in ignored_directories
        ]

        for directory in list(dirs):

            if not directory.endswith(
                ".xcassets"
            ):
                continue

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

            # ------------------------------------------------
            # xcassets içine girme.
            # ------------------------------------------------

            dirs.remove(
                directory
            )

    assets.sort(
        key=lambda item: item["relative_path"].lower()
    )

    return assets


# ============================================================
# ASSET CATALOG VALIDATION
# ============================================================

def validate_asset_catalogs(asset_catalogs):

    print()
    print("============================================")
    print(" ASSET CATALOG KONTROLÜ")
    print("============================================")

    for item in asset_catalogs:

        catalog = item["full_path"]

        print(
            "  ✓",
            item["relative_path"]
        )

        # ----------------------------------------------------
        # Empty AppIcon.appiconset detection
        # ----------------------------------------------------

        app_icon = os.path.join(
            catalog,
            "AppIcon.appiconset"
        )

        contents = os.path.join(
            app_icon,
            "Contents.json"
        )

        if os.path.isdir(
            app_icon
        ):

            if os.path.isfile(
                contents
            ):

                try:

                    with open(
                        contents,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read().strip()

                    # ------------------------------------------------
                    # Empty icon set.
                    #
                    # We DO NOT configure AppIcon in the generated
                    # target, but actool may still inspect invalid
                    # catalog data. Warn clearly.
                    # ------------------------------------------------

                    if '"images"' in content and '"images" : []' in content:

                        print()
                        print(
                            "  WARNING: Boş AppIcon.appiconset bulundu:"
                        )

                        print(
                            "   ",
                            os.path.relpath(
                                app_icon,
                                SOURCE_ROOT
                            )
                        )

                        print(
                            "  AppIcon kullanılmayacağı için"
                        )

                        print(
                            "  ASSETCATALOG_COMPILER_APPICON_NAME"
                        )

                        print(
                            "  build setting'i eklenmeyecek."
                        )

                except Exception as error:

                    print(
                        "  WARNING: AppIcon Contents.json okunamadı:",
                        error
                    )

    return True


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
        ".cxx"
    }


def is_header_file(path):

    extension = os.path.splitext(
        path
    )[1].lower()

    return extension in {
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
    # DIRECTORY
    #
    # Example:
    #
    # App/AppDelegate.swift
    #
    # group_path = App
    # file_name = AppDelegate.swift
    # --------------------------------------------------------

    group_path = normalize(
        os.path.dirname(
            relative_path
        )
    )

    group = ensure_group(
        data,
        group_path
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # PBXFileReference.path is relative to its PBXGroup.
    #
    # Correct:
    #
    # App group:
    #     path = AppDelegate.swift
    #
    # Incorrect:
    #     path = App/AppDelegate.swift
    #
    # This prevents:
    #
    # App/App/AppDelegate.swift
    # --------------------------------------------------------

    file_name = item["filename"]

    file_id = make_uuid(
        "file:" + relative_path
    )

    file_reference = {
        "id": file_id,
        "path": file_name,
        "relative_path": relative_path,
        "name": file_name,
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
    # SOURCE
    # --------------------------------------------------------

    if is_source_file(
        relative_path
    ):

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

    # --------------------------------------------------------
    # HEADER
    #
    # Header files remain visible in Xcode but are NOT
    # compiled as source files.
    # --------------------------------------------------------

    elif is_header_file(
        relative_path
    ):

        pass

    # --------------------------------------------------------
    # RESOURCE
    # --------------------------------------------------------

    elif is_resource_file(
        relative_path
    ):

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
        os.path.dirname(
            relative_path
        )
    )

    group = ensure_group(
        data,
        group_path
    )

    file_name = item["filename"]

    file_id = make_uuid(
        "file:" + relative_path
    )

    file_reference = {
        "id": file_id,
        "path": file_name,
        "relative_path": relative_path,
        "name": file_name,
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
# FILE TYPE FOR PBX
# ============================================================

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

    if lower.endswith(".html"):
        return "text.html"

    if lower.endswith(".css"):
        return "text.css"

    if lower.endswith(".js"):
        return "sourcecode.javascript"

    return "text"


# ============================================================
# EMIT GROUP
# ============================================================

def emit_group(
    lines,
    group,
    level=2
):

    children = []

    # --------------------------------------------------------
    # CHILD GROUPS
    # --------------------------------------------------------

    for child in group.children:

        children.append(
            "{} /* {} */".format(
                child.id,
                child.name
            )
        )

    # --------------------------------------------------------
    # FILES
    # --------------------------------------------------------

    for file_ref in group.files:

        children.append(
            "{} /* {} */".format(
                file_ref["id"],
                file_ref["name"]
            )
        )

    # --------------------------------------------------------
    # GROUP HEADER
    # --------------------------------------------------------

    lines.append(
        "{}{} /* {} */ = {{isa = PBXGroup; "
        "children = (\n".format(
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

    # --------------------------------------------------------
    # ROOT
    # --------------------------------------------------------

    if group.is_root:

        lines.append(
            "{}); "
            "name = \"{}\"; "
            "sourceTree = \"<group>\"; "
            "}};".format(
                indent(level),
                xcode_quote(
                    group.name
                )
            )
        )

    # --------------------------------------------------------
    # NORMAL GROUP
    # --------------------------------------------------------

    else:

        lines.append(
            "{}); "
            "name = \"{}\"; "
            "path = \"{}\"; "
            "sourceTree = \"<group>\"; "
            "}};".format(
                indent(level),
                xcode_quote(
                    group.name
                ),
                xcode_quote(
                    group.path or ""
                )
            )
        )

    # --------------------------------------------------------
    # CHILDREN
    # --------------------------------------------------------

    for child in group.children:

        # Products ayrı PBXGroup olarak emit ediliyor.
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
    file_reference,
    phase_name
):

    lines.append(
        "\t\t{} /* {} in {} */ = "
        "{{isa = PBXBuildFile; "
        "fileRef = {} /* {} */; }};".format(
            build_file["id"],
            file_reference["name"],
            phase_name,
            file_reference["id"],
            file_reference["name"]
        )
    )


# ============================================================
# SOURCES PHASE
# ============================================================

def emit_sources_phase(
    lines,
    data
):

    lines.append(
        "\t\t{} /* Sources */ = "
        "{{isa = PBXSourcesBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n".format(
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
        "};"
    )


# ============================================================
# FRAMEWORKS PHASE
# ============================================================

def emit_frameworks_phase(
    lines,
    data
):

    lines.append(
        "\t\t{} /* Frameworks */ = "
        "{{isa = PBXFrameworksBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n".format(
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
        "};"
    )


# ============================================================
# RESOURCES PHASE
# ============================================================

def emit_resources_phase(
    lines,
    data
):

    lines.append(
        "\t\t{} /* Resources */ = "
        "{{isa = PBXResourcesBuildPhase; "
        "buildActionMask = 2147483647; "
        "files = (\n".format(
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

    # --------------------------------------------------------
    # Info.plist intentionally NOT added to Resources.
    # --------------------------------------------------------

    lines.append(
        "\t\t); "
        "runOnlyForDeploymentPostprocessing = 0; "
        "};"
    )


# ============================================================
# CONFIGURATION LISTS
# ============================================================

def emit_configuration_lists(
    lines,
    data
):

    lines.append(
        "\t\t{} /* Build configuration list for PBXProject \"{}\" */ = "
        "{{isa = XCConfigurationList; "
        "buildConfigurations = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "defaultConfigurationIsVisible = 0; "
        "defaultConfigurationName = Release; "
        "}};".format(
            data.configuration_list_project_id,
            PROJECT_NAME,
            data.debug_project_config_id,
            data.release_project_config_id
        )
    )

    lines.append("")

    lines.append(
        "\t\t{} /* Build configuration list for PBXNativeTarget \"{}\" */ = "
        "{{isa = XCConfigurationList; "
        "buildConfigurations = (\n"
        "\t\t\t{},\n"
        "\t\t\t{},\n"
        "\t\t); "
        "defaultConfigurationIsVisible = 0; "
        "defaultConfigurationName = Release; "
        "}};".format(
            data.configuration_list_target_id,
            TARGET_NAME,
            data.debug_target_config_id,
            data.release_target_config_id
        )
    )


# ============================================================
# PROJECT DEBUG CONFIGURATION
# ============================================================

def emit_project_debug_configuration(
    lines,
    data
):

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
        "}};".format(
            data.debug_project_config_id
        )
    )


# ============================================================
# PROJECT RELEASE CONFIGURATION
# ============================================================

def emit_project_release_configuration(
    lines,
    data
):

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
        "}};".format(
            data.release_project_config_id
        )
    )


# ============================================================
# TARGET CONFIGURATION
# ============================================================

def emit_target_configuration(
    lines,
    config_id,
    config_name
):

    # --------------------------------------------------------
    # NO .format() HERE.
    #
    # This prevents:
    #
    # IndexError: Replacement index 3 out of range
    # --------------------------------------------------------

    lines.append(
        "\t\t"
        + config_id
        + " /* "
        + config_name
        + " */ = {isa = XCBuildConfiguration;"
    )

    lines.append(
        "\t\t\tbuildSettings = {"
    )

    lines.append(
        "\t\t\t\tCLANG_ENABLE_MODULES = YES;"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # AppIcon build setting intentionally removed.
    #
    # There is no:
    #
    # ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
    #
    # Therefore an empty AppIcon set is not referenced as the
    # application's icon.
    # --------------------------------------------------------

    lines.append(
        "\t\t\t\tCODE_SIGN_STYLE = Automatic;"
    )

    lines.append(
        "\t\t\t\tCURRENT_PROJECT_VERSION = 1;"
    )

    lines.append(
        "\t\t\t\tDEVELOPMENT_TEAM = \"\";"
    )

    lines.append(
        "\t\t\t\tGENERATE_INFOPLIST_FILE = NO;"
    )

    # --------------------------------------------------------
    # INFO.PLIST
    #
    # xcodebuild runs from the repository root.
    #
    # Therefore:
    #
    # AsasecIl2cppDumper-Gui-App/Info.plist
    # --------------------------------------------------------

    lines.append(
        "\t\t\t\tINFOPLIST_FILE = \""
        + xcode_quote(
            APP_DIRECTORY
        )
        + "/Info.plist\";"
    )

    lines.append(
        "\t\t\t\tINFOPLIST_KEY_CFBundleDisplayName = \""
        + xcode_quote(
            TARGET_NAME
        )
        + "\";"
    )

    # --------------------------------------------------------
    # Launch Screen
    #
    # The physical file is:
    #
    # AsasecIl2cppDumper-Gui-App/LaunchScreen.storyboard
    #
    # Xcode resolves "LaunchScreen" to that storyboard.
    # --------------------------------------------------------

    lines.append(
        "\t\t\t\tINFOPLIST_KEY_UILaunchStoryboardName = LaunchScreen;"
    )

    lines.append(
        "\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 13.0;"
    )

    lines.append(
        "\t\t\t\tLD_RUNPATH_SEARCH_PATHS = ("
    )

    lines.append(
        "\t\t\t\t\t\"$(inherited)\","
    )

    lines.append(
        "\t\t\t\t\t\"@executable_path/Frameworks\","
    )

    lines.append(
        "\t\t\t\t);"
    )

    lines.append(
        "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = "
        + BUNDLE_IDENTIFIER
        + ";"
    )

    lines.append(
        "\t\t\t\tPRODUCT_NAME = \"$(TARGET_NAME)\";"
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
        "\t\t\tname = "
        + config_name
        + ";"
    )

    lines.append(
        "\t\t};"
    )


# ============================================================
# GENERATE PROJECT
# ============================================================

def generate_project(data):

    lines = []

    # ========================================================
    # HEADER
    # ========================================================

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

    # ========================================================
    # PBX BUILD FILES
    # ========================================================

    for relative_path, build_file in data.build_files.items():

        file_ref = data.file_references[
            relative_path
        ]

        if build_file in data.resource_build_files:

            phase_name = "Resources"

        elif build_file in data.framework_build_files:

            phase_name = "Frameworks"

        else:

            phase_name = "Sources"

        emit_build_file(
            lines,
            build_file,
            file_ref,
            phase_name
        )

    # ========================================================
    # PBX FILE REFERENCES
    # ========================================================

    for relative_path, file_ref in data.file_references.items():

        lines.append(
            "\t\t{} /* {} */ = "
            "{{isa = PBXFileReference; "
            "fileEncoding = 4; "
            "lastKnownFileType = {}; "
            "path = \"{}\"; "
            "sourceTree = \"<group>\"; }};".format(
                file_ref["id"],
                file_ref["name"],
                file_type_for_path(
                    relative_path
                ),
                xcode_quote(
                    file_ref["path"]
                )
            )
        )

    # ========================================================
    # INFO.PLIST FILE REFERENCE
    # ========================================================

    lines.append(
        "\t\t{} /* Info.plist */ = "
        "{{isa = PBXFileReference; "
        "fileEncoding = 4; "
        "lastKnownFileType = text.plist.xml; "
        "path = \"Info.plist\"; "
        "sourceTree = \"<group>\"; }};".format(
            data.info_plist_file_reference_id
        )
    )

    # ========================================================
    # APPLICATION PRODUCT
    # ========================================================

    lines.append(
        "\t\t{} /* {}.app */ = "
        "{{isa = PBXFileReference; "
        "explicitFileType = wrapper.application; "
        "includeInIndex = 0; "
        "path = \"{}.app\"; "
        "sourceTree = BUILT_PRODUCTS_DIR; }};".format(
            data.app_file_reference_id,
            TARGET_NAME,
            TARGET_NAME
        )
    )

    # ========================================================
    # GROUPS
    # ========================================================

    emit_group(
        lines,
        data.root_group,
        level=2
    )

    # ========================================================
    # PRODUCTS GROUP
    # ========================================================

    lines.append(
        "\t\t{} /* Products */ = "
        "{{isa = PBXGroup; "
        "children = (\n"
        "\t\t\t{} /* {}.app */,\n"
        "\t\t); "
        "name = Products; "
        "sourceTree = \"<group>\"; }};".format(
            data.products_group_id,
            data.app_file_reference_id,
            TARGET_NAME
        )
    )

    # ========================================================
    # NATIVE TARGET
    # ========================================================

    lines.append(
        "\t\t{} /* {} */ = "
        "{{isa = PBXNativeTarget; "
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
        "}};".format(
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
    # PROJECT OBJECT
    # ========================================================

    lines.append(
        "\t\t{} /* Project object */ = "
        "{{isa = PBXProject; "
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
        "}};".format(
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

    emit_sources_phase(
        lines,
        data
    )

    emit_frameworks_phase(
        lines,
        data
    )

    emit_resources_phase(
        lines,
        data
    )

    # ========================================================
    # PROJECT CONFIGURATIONS
    # ========================================================

    emit_project_debug_configuration(
        lines,
        data
    )

    emit_project_release_configuration(
        lines,
        data
    )

    # ========================================================
    # TARGET CONFIGURATIONS
    # ========================================================

    emit_target_configuration(
        lines,
        data.debug_target_config_id,
        "Debug"
    )

    emit_target_configuration(
        lines,
        data.release_target_config_id,
        "Release"
    )

    # ========================================================
    # CONFIGURATION LISTS
    # ========================================================

    emit_configuration_lists(
        lines,
        data
    )

    # ========================================================
    # END OBJECTS
    # ========================================================

    lines.append(
        "\t};"
    )

    lines.append(
        "\trootObject = {} /* Project object */;".format(
            data.project_id
        )
    )

    lines.append(
        "}"
    )

    # ========================================================
    # WRITE PROJECT
    # ========================================================

    os.makedirs(
        PROJECT_DIRECTORY,
        exist_ok=True
    )

    with open(
        PROJECT_FILE,
        "w",
        encoding="utf-8"
    ) as project_file:

        project_file.write(
            "\n".join(lines)
        )

        project_file.write(
            "\n"
        )


# ============================================================
# VALIDATE GENERATED PATHS
# ============================================================

def validate_project_paths(data):

    print()
    print("============================================")
    print(" PBX PATH KONTROLÜ")
    print("============================================")

    problems = 0

    for relative_path, file_ref in sorted(
        data.file_references.items()
    ):

        group_path = ""

        # ----------------------------------------------------
        # FIND ACTUAL GROUP PATH
        # ----------------------------------------------------

        for directory, group in data.group_map.items():

            if group.id == file_ref["group"]:

                group_path = directory

                break

        # ----------------------------------------------------
        # CALCULATE EXPECTED PATH
        # ----------------------------------------------------

        if group_path:

            expected = normalize(
                group_path
                + "/"
                + file_ref["path"]
            )

        else:

            expected = normalize(
                file_ref["path"]
            )

        # ----------------------------------------------------
        # COMPARE
        # ----------------------------------------------------

        if expected != relative_path:

            problems += 1

            print(
                "  ✗ ERROR:",
                relative_path
            )

            print(
                "    PBX:",
                expected
            )

            print(
                "    REF:",
                file_ref["path"]
            )

        else:

            print(
                "  ✓",
                relative_path
            )

    if problems == 0:

        print()
        print(
            "Tüm PBX dosya yolları doğru."
        )

    else:

        print()
        print(
            "HATALI PATH SAYISI:",
            problems
        )

    return problems


# ============================================================
# VALIDATE LAUNCHSCREEN PBX ENTRY
# ============================================================

def validate_launch_screen_pbx(data):

    print()
    print("============================================")
    print(" LAUNCHSCREEN PBX KONTROLÜ")
    print("============================================")

    relative_path = "LaunchScreen.storyboard"

    file_ref = data.file_references.get(
        relative_path
    )

    if file_ref is None:

        print(
            "  ✗ LaunchScreen.storyboard PBX içinde yok."
        )

        return 1

    # --------------------------------------------------------
    # It MUST be in root group.
    # --------------------------------------------------------

    if file_ref["group"] != data.root_group_id:

        print(
            "  ✗ LaunchScreen.storyboard root group içinde değil."
        )

        print(
            "    Group ID:",
            file_ref["group"]
        )

        return 1

    # --------------------------------------------------------
    # It MUST only contain basename.
    # --------------------------------------------------------

    if file_ref["path"] != "LaunchScreen.storyboard":

        print(
            "  ✗ LaunchScreen PBX path yanlış:",
            file_ref["path"]
        )

        return 1

    print(
        "  ✓ LaunchScreen.storyboard"
    )

    print(
        "    Group : ROOT"
    )

    print(
        "    Path  : LaunchScreen.storyboard"
    )

    print(
        "    Disk  :",
        os.path.abspath(
            os.path.join(
                SOURCE_ROOT,
                relative_path
            )
        )
    )

    return 0


# ============================================================
# PRINT FINAL TREE
# ============================================================

def print_source_tree():

    print()
    print("============================================")
    print(" GERÇEK KAYNAK AĞACI")
    print("============================================")

    if not os.path.isdir(
        SOURCE_ROOT
    ):

        print(
            "SOURCE_ROOT bulunamadı."
        )

        return

    for root, dirs, files in os.walk(
        SOURCE_ROOT
    ):

        dirs[:] = sorted(
            [
                d
                for d in dirs
                if d not in {
                    ".git",
                    ".github",
                    "build",
                    "DerivedData",
                    ".build",
                    "__pycache__",
                    ".xcodeproj"
                }
            ]
        )

        files = sorted(
            files
        )

        relative_root = normalize(
            os.path.relpath(
                root,
                SOURCE_ROOT
            )
        )

        if relative_root == "":

            prefix = ""

        else:

            prefix = relative_root + "/"

        for filename in files:

            if filename.startswith("."):
                continue

            print(
                "  ",
                prefix + filename
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("============================================")
    print(" Asasec Xcode Project Generator")
    print("============================================")

    print(
        "Project :",
        PROJECT_NAME
    )

    print(
        "Target  :",
        TARGET_NAME
    )

    print(
        "Bundle  :",
        BUNDLE_IDENTIFIER
    )

    print(
        "Source  :",
        SOURCE_ROOT
    )

    print()

    # ========================================================
    # CHECK SOURCE ROOT
    # ========================================================

    if not os.path.isdir(
        SOURCE_ROOT
    ):

        print(
            "ERROR: Kaynak klasörü bulunamadı:"
        )

        print(
            os.path.abspath(
                SOURCE_ROOT
            )
        )

        return 1

    # ========================================================
    # REQUIRED FILES
    # ========================================================

    if not validate_required_files():

        print()
        print(
            "Generator durduruldu."
        )

        return 1

    # ========================================================
    # LAUNCHSCREEN
    # ========================================================

    if not validate_launch_screen_file():

        print()
        print(
            "ERROR: LaunchScreen.storyboard geçersiz."
        )

        return 1

    # ========================================================
    # INFO.PLIST
    # ========================================================

    if not validate_info_plist_file():

        print()
        print(
            "ERROR: Info.plist geçersiz."
        )

        return 1

    # ========================================================
    # CLEAN OLD PROJECT
    # ========================================================

    if os.path.isdir(
        PROJECT_DIRECTORY
    ):

        print(
            "Eski Xcode projesi siliniyor..."
        )

        shutil.rmtree(
            PROJECT_DIRECTORY
        )

    # ========================================================
    # CREATE DATA
    # ========================================================

    data = ProjectData()

    # ========================================================
    # CREATE GROUP TREE
    # ========================================================

    create_group_tree(
        data
    )

    # ========================================================
    # SCAN NORMAL FILES
    # ========================================================

    project_files = scan_project_files()

    print()
    print(
        "Kaynak / resource dosyaları:",
        len(project_files)
    )

    launch_screen_found = False

    for item in project_files:

        print(
            "  FILE",
            item["relative_path"]
        )

        if item["relative_path"] == "LaunchScreen.storyboard":

            launch_screen_found = True

        add_file(
            data,
            item
        )

    # ========================================================
    # LAUNCHSCREEN MUST BE SCANNED
    # ========================================================

    if not launch_screen_found:

        print()
        print(
            "ERROR: LaunchScreen.storyboard scan sonucunda yok."
        )

        print(
            "Beklenen:"
        )

        print(
            " ",
            os.path.abspath(
                os.path.join(
                    SOURCE_ROOT,
                    "LaunchScreen.storyboard"
                )
            )
        )

        return 1

    # ========================================================
    # SCAN ASSET CATALOGS
    # ========================================================

    asset_catalogs = scan_asset_catalogs()

    print()
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

    # ========================================================
    # VALIDATE ASSETS
    # ========================================================

    validate_asset_catalogs(
        asset_catalogs
    )

    # ========================================================
    # VERIFY LAUNCHSCREEN PBX DATA BEFORE GENERATION
    # ========================================================

    launch_pbx_error = validate_launch_screen_pbx(
        data
    )

    if launch_pbx_error != 0:

        print()
        print(
            "ERROR: LaunchScreen PBX doğrulaması başarısız."
        )

        return 1

    # ========================================================
    # GENERATE
    # ========================================================

    print()
    print(
        "Xcode project oluşturuluyor..."
    )

    generate_project(
        data
    )

    # ========================================================
    # VALIDATE PATHS
    # ========================================================

    path_errors = validate_project_paths(
        data
    )

    # ========================================================
    # VERIFY GENERATED PROJECT FILE
    # ========================================================

    project_exists = os.path.isfile(
        PROJECT_FILE
    )

    if not project_exists:

        print()
        print(
            "ERROR: project.pbxproj oluşturulamadı."
        )

        return 1

    print()
    print("============================================")
    print(" GENERATED PROJECT KONTROLÜ")
    print("============================================")

    print(
        "  ✓",
        os.path.abspath(
            PROJECT_FILE
        )
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("============================================")

    if path_errors == 0:

        print(
            " Xcode project başarıyla oluşturuldu"
        )

    else:

        print(
            " Xcode project oluşturuldu fakat"
        )

        print(
            " path kontrolünde hata bulundu"
        )

    print("============================================")

    print(
        "Project:",
        os.path.abspath(
            PROJECT_DIRECTORY
        )
    )

    print()

    print(
        "Build kaynakları:",
        len(
            data.source_build_files
        )
    )

    print(
        "Resources:",
        len(
            data.resource_build_files
        )
    )

    print(
        "Frameworks:",
        len(
            data.framework_build_files
        )
    )

    print()

    print(
        "Kontrol edilen dosya yolları:"
    )

    for relative_path in sorted(
        data.file_references.keys()
    ):

        print(
            "  ✓",
            relative_path
        )

    print_source_tree()

    print()

    print(
        "Eski .xcodeproj silindi."
    )

    print(
        "Yeni .xcodeproj oluşturuldu."
    )

    print()

    if path_errors != 0:

        return 1

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
