from lxml import etree
import os
import sys
import uuid

# Automatically generate Visual Studio project files.
# Include Paths, .h and .cpp files are generated based on subfolder structure relative to this script.
# This script should be placed in the same folder where YOUR_PROJECT.vcxproj file is
# Compatible with Visual Studio Community 2022

# ==================================================
#                   EDIT HERE
# ==================================================

project_name = "YOUR_PROJECT_NAME"     # name of the project
project_guid = "{YOUR_PROJECT_ID}"     # project ID

additional_include_paths = []
additional_header_files = []
additional_source_files = []

output_directory = "Build"
intermediate_directory = "Intermediate"

ignore_folders = ["Build", "Intermediate"]

# If True, Console will stay open after running the script
bAutoCloseConsole = True


# ==================================================
#                  GET SUBFOLDERS
# ==================================================

def get_subfolders_and_files(root_dir):
    subfolders = []
    h_files = []
    cpp_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Get relative directory path
        rel_dirpath = os.path.relpath(dirpath, root_dir)      

         # Skip folders specified in ignore_folders
        if any(rel_dirpath.startswith(folder) for folder in ignore_folders):
            continue

        # Append subfolder path
        if rel_dirpath != ".":
            subfolders.append(rel_dirpath)

        # Append .h and .cpp files with relative paths
        for filename in filenames:
            if filename.endswith(".h"):
                h_files.append(os.path.join(rel_dirpath, filename))
            elif filename.endswith(".cpp"):
                cpp_files.append(os.path.join(rel_dirpath, filename))

    return subfolders, h_files, cpp_files


# Get the directory of the current script
script_directory = os.path.dirname(os.path.abspath(__file__))
subfolders, header_files, source_files = get_subfolders_and_files(script_directory)

subfolders.extend(additional_include_paths)
header_files.extend(additional_header_files)
source_files.extend(additional_source_files)

include_directories = ";".join(subfolders) + ";%(AdditionalIncludeDirectories)"


# ==================================================
#                vxcproj file
# ==================================================

def create_vcxproj_file(output_path):
    # Create the root element: Project
    project = etree.Element("Project", {
        "DefaultTargets": "Build",
        "ToolsVersion": "15.0",
        "xmlns": "http://schemas.microsoft.com/developer/msbuild/2003"
    })

    # Add an ItemGroup element with ProjectConfiguration elements
    item_group_configurations = etree.SubElement(project, "ItemGroup", {"Label": "ProjectConfigurations"})
    configurations = [
        {"Include": "Debug|Win32", "Configuration": "Debug", "Platform": "Win32"},
        {"Include": "Release|Win32", "Configuration": "Release", "Platform": "Win32"},
        {"Include": "Debug|x64", "Configuration": "Debug", "Platform": "x64"},
        {"Include": "Release|x64", "Configuration": "Release", "Platform": "x64"}
    ]
    for config in configurations:
        project_config = etree.SubElement(item_group_configurations, "ProjectConfiguration", {"Include": config["Include"]})
        etree.SubElement(project_config, "Configuration").text = config["Configuration"]
        etree.SubElement(project_config, "Platform").text = config["Platform"]

    # Add an ItemGroup element with a ClCompile element for each source file
    item_group_sources = etree.SubElement(project, "ItemGroup")
    #source_files = ["GenerateIncludesTargetProject.cpp", "Array/Array.cpp", "Debug/Debug.cpp"]
    for src_file in source_files:
        etree.SubElement(item_group_sources, "ClCompile", {"Include": src_file})

    # Add an ItemGroup element with a ClInclude element for each header file
    item_group_headers = etree.SubElement(project, "ItemGroup")
    #header_files = ["Array/Array.h", "Debug/Debug.h"]
    for hdr_file in header_files:
        etree.SubElement(item_group_headers, "ClInclude", {"Include": hdr_file})

    # Add a PropertyGroup element with basic configuration properties
    property_group = etree.SubElement(project, "PropertyGroup", {"Label": "Globals"})
    etree.SubElement(property_group, "ProjectGuid").text = project_guid
    etree.SubElement(property_group, "RootNamespace").text = project_name
    etree.SubElement(property_group, "Keyword").text = "Win32Proj"
    etree.SubElement(property_group, "VCProjectVersion").text = "16.0"
    etree.SubElement(property_group, "WindowsTargetPlatformVersion").text = "10.0"

    # Add a PropertyGroup element with ConfigurationType, UseDebugLibraries, PlatformToolset, and CharacterSet for each configuration
    config_conditions = [
        "'$(Configuration)|$(Platform)'=='Debug|Win32'",
        "'$(Configuration)|$(Platform)'=='Release|Win32'",
        "'$(Configuration)|$(Platform)'=='Debug|x64'",
        "'$(Configuration)|$(Platform)'=='Release|x64'"
    ]
    config_types = [
        {
            "ConfigurationType": "Application",
            "UseDebugLibraries": "true",
            "PlatformToolset": "v143",
            "CharacterSet": "Unicode"
        },
        {
            "ConfigurationType": "Application",
            "UseDebugLibraries": "false",
            "PlatformToolset": "v143",
            "WholeProgramOptimization": "true",
            "CharacterSet": "Unicode"
        },
        {
            "ConfigurationType": "Application",
            "UseDebugLibraries": "true",
            "PlatformToolset": "v143",
            "CharacterSet": "Unicode"
        },
        {
            "ConfigurationType": "Application",
            "UseDebugLibraries": "false",
            "PlatformToolset": "v143",
            "WholeProgramOptimization": "true",
            "CharacterSet": "Unicode"
        }
    ]
    for i, condition in enumerate(config_conditions):
        property_group_config = etree.SubElement(project, "PropertyGroup", {"Condition": condition, "Label": "Configuration"})
        etree.SubElement(property_group_config, "ConfigurationType").text = config_types[i]["ConfigurationType"]
        etree.SubElement(property_group_config, "UseDebugLibraries").text = config_types[i]["UseDebugLibraries"]
        etree.SubElement(property_group_config, "PlatformToolset").text = config_types[i]["PlatformToolset"]
        etree.SubElement(property_group_config, "CharacterSet").text = config_types[i]["CharacterSet"]
        if "WholeProgramOptimization" in config_types[i]:
            etree.SubElement(property_group_config, "WholeProgramOptimization").text = config_types[i]["WholeProgramOptimization"]         
        # Add output and intermediate directories       
        etree.SubElement(property_group_config, "OutDir").text = f"{output_directory}/{configurations[i]['Platform']}/{configurations[i]['Configuration']}/"
        etree.SubElement(property_group_config, "IntDir").text = f"{intermediate_directory}/{configurations[i]['Platform']}/{configurations[i]['Configuration']}/"   

    # Import Microsoft.Cpp.Default.props and Microsoft.Cpp.props
    import_cpp_default_props = etree.SubElement(project, "Import", {"Project": "$(VCTargetsPath)\\Microsoft.Cpp.Default.props"})
    import_cpp_props = etree.SubElement(project, "Import", {"Project": "$(VCTargetsPath)\\Microsoft.Cpp.props"})

    # Aby konzolu hned nezatvorilo pri Ctrl+F5
    linker_subsystem_conditions = [
        "'$(Configuration)|$(Platform)'=='Debug|Win32'",
        "'$(Configuration)|$(Platform)'=='Release|Win32'",
        "'$(Configuration)|$(Platform)'=='Debug|x64'",
        "'$(Configuration)|$(Platform)'=='Release|x64'"
    ]
    for i, condition in enumerate(linker_subsystem_conditions):
        item_definition_group = etree.SubElement(project, "ItemDefinitionGroup", {"Condition": condition})
        cl_compile = etree.SubElement(item_definition_group, "ClCompile")
        #etree.SubElement(cl_compile, "AdditionalIncludeDirectories").text = "Stopwatch;%(AdditionalIncludeDirectories)"#include_directories
        etree.SubElement(cl_compile, "AdditionalIncludeDirectories").text = include_directories
        link = etree.SubElement(item_definition_group, "Link")
        etree.SubElement(link, "SubSystem").text = "Console"

    # Import Microsoft.Cpp.targets
    import_cpp_targets = etree.SubElement(project, "Import", {"Project": "$(VCTargetsPath)\\Microsoft.Cpp.targets"})

    # Write the output XML
    with open(output_path, "wb") as f:
        f.write(etree.tostring(project, pretty_print=True, xml_declaration=True, encoding="utf-8"))


# ==================================================
#               vxcproj filter file
# ==================================================

def create_vcxproj_filters_file(output_path):
    # Create the root element: Project
    project = etree.Element("Project", {
        "ToolsVersion": "4.0",
        "xmlns": "http://schemas.microsoft.com/developer/msbuild/2003"
    })

    # Add an ItemGroup element with Filter elements for each subfolder
    item_group_filters = etree.SubElement(project, "ItemGroup")
    for subfolder in subfolders:
        etree.SubElement(item_group_filters, "Filter", {
            "Include": subfolder,
            "UniqueIdentifier": "{%s}" % uuid.uuid4()  # Generate a random GUID for each filter
        })

    # Add an ItemGroup element with ClCompile elements for each .cpp file
    item_group_sources = etree.SubElement(project, "ItemGroup")
    for src_file in source_files:
        cl_compile = etree.SubElement(item_group_sources, "ClCompile", {"Include": src_file})
        src_file_folder = os.path.dirname(src_file)
        if src_file_folder:
            etree.SubElement(cl_compile, "Filter").text = src_file_folder

    # Add an ItemGroup element with ClInclude elements for each .h file
    item_group_headers = etree.SubElement(project, "ItemGroup")
    for hdr_file in header_files:
        cl_include = etree.SubElement(item_group_headers, "ClInclude", {"Include": hdr_file})
        hdr_file_folder = os.path.dirname(hdr_file)
        if hdr_file_folder:
            etree.SubElement(cl_include, "Filter").text = hdr_file_folder

    # Write the output XML
    with open(output_path, "wb") as f:
        f.write(etree.tostring(project, pretty_print=True, xml_declaration=True, encoding="utf-8"))


# ==================================================
#                     main
# ==================================================

if __name__ == "__main__":       
    output_path = f"{project_name}.vcxproj"   
    output_filters_path = f"{project_name}.vcxproj.filters"

    create_vcxproj_file(output_path)   
    create_vcxproj_filters_file(output_filters_path)

    print(f"File {output_path} created.")
    print(f"File {output_filters_path} created.")

if not bAutoCloseConsole: 
    input("Press Enter to exit...")
    sys.exit()