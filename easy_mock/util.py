# -*- coding: utf-8 -*-
import json
import os


class ApiStruct:
    def __init__(self):
        self.name = ""
        self.uri = ""
        self.method = "POST"
        self.req_class = ""
        self.res_class = ""
        self.req_schema = ""
        self.res_schema = ""

    def __str__(self):
        return self.name + " " + self.req_class + " " + self.res_class + " " + self.method + " " + self.uri


class Pb2Yaml:
    @classmethod
    def pb2ymal(cls, pb_file_name, req_schema=True, res_schema=True):
        if not os.path.isfile(pb_file_name) or not pb_file_name.endswith(".proto"):
            print("Invalid file " + str(pb_file_name))

        print("Converting proto file to yaml file: " + pb_file_name)
        with open(pb_file_name, "r") as pb:
            api_struct_list = cls.get_api_list(pb)
            pb.seek(0)
            pb_content = pb.readlines()
            cls.get_schema(pb_content, api_struct_list)
            cls.generate_yml_file(api_struct_list, pb_file_name, req_schema=req_schema, res_schema=res_schema)

    @classmethod
    def get_schema(cls, pb, api_struct_list):
        class_blob_dict = cls.get_class_blob_from_pb(pb)

        for api in api_struct_list:
            api.req_schema = cls.generate_class_schema(class_blob_dict[api.req_class])
            api.res_schema = cls.generate_class_schema(class_blob_dict[api.res_class])

    @classmethod
    def generate_class_schema(cls, class_blob):
        pb_type_list = ["bool", "string", "bytes", "double", "float", "int32", "int64", "uint32",
                        "uint64", "sint32", "sint64", "fixed32", "fixed64", "sfixed32", "sfixed64"]

        line = class_blob[0].lstrip()
        is_enum = line.startswith("enum ")

        class_name = line.split(" ")[1]
        class_name = class_name.replace("{", "").replace("\n", "")

        class_body = [4 * " " + "{\n", 8 * " " + "\"type\": \"object\",\n",
                      8 * " " + "\"title\": " + "\"The " + class_name + " Schema\",\n",
                      8 * " " + "\"required\": [], \n",
                      8 * " " + "\"properties\": {\n"]

        class_content = []

        # deal with empty response class: XXXResponse{}, which has only two line
        if 2 == len(class_blob) and line.endswith("}"):
            class_content.append(4 * " " + "pass\n")
            return class_content

        for line in class_blob[1:]:
            line = line.strip()

            if line.endswith("}"):
                break

            class_field = " " * 4 + line.replace(";", "") + "\n"

            # separate line by space,   such as line : repeated string name = 10;
            split_list = line.split(" ")
            is_ary = False

            if "reserved" == split_list[0]:
                continue

            if "repeated" == split_list[0]:
                is_ary = True
                para_filed_annotation = "repeated " + split_list[1]
                para_type = split_list[1]
                para_name = split_list[2]
                para_cmt = split_list[3:]
            else:
                para_filed_annotation = split_list[0]
                para_type = split_list[0]
                para_name = split_list[1]
                para_cmt = split_list[2:]

            class_body.append(12 * " " + "\"" + para_name + "\": {\n")
            schema_type = para_type

            type_name_changed = False

            if not (para_type in pb_type_list):
                schema_type = "object"
                type_name_changed = True

            if schema_type == "bool":
                schema_type = "boolean"
                type_name_changed = True

            if schema_type == "bytes":
                schema_type = "string"
                type_name_changed = True

            if -1 != schema_type.find("int") or -1 != schema_type.find("fixed"):
                schema_type = "integer"
                type_name_changed = True

            if schema_type == "double" or schema_type == "float":
                schema_type = "number"
                type_name_changed = True

            if is_ary:
                schema_type = "array"

            if type_name_changed:
                class_body.append(16 * " " + "\"type\": \"" + schema_type + "\",  # " + para_type + "\n")
            else:
                class_body.append(16 * " " + "\"type\": \"" + schema_type + "\",\n")

            if is_ary:
                class_body.append(16 * " " + "\"items\": [\n")
                class_body.append(20 * " " + "{\n")
                class_body.append(24 * " " + "\"type\": \"object\"," + "  # " + para_type + "\n")
                class_body.append(20 * " " + "},\n")
                class_body.append(16 * " " + "]\n")

            class_body.append(12 * " " + "},\n")

        class_body.append(8 * " " + "}\n")
        class_body.append(4 * " " + "}\n")
        class_content.extend(class_body)
        return class_content

    @classmethod
    def generate_yml_file(cls, api_list, pb_file_name, req_schema=True, res_schema=True):

        yaml_file = os.path.basename(pb_file_name).split(".")[0]
        output_file = yaml_file + ".yml"
        print("Writing to file : " + output_file)
        with open("./" + output_file, "w+") as yml_file:
            yml_file.write("apis:\n")
            for api in api_list:
                yml_file.write("  - url: " + api.uri.strip() + "\n")
                yml_file.write("    method: " + api.method + "\n")
                yml_file.write("    name: " + api.name + "\n")

                if req_schema:
                    yml_file.write("    request_schema: \n")
                    for line in api.req_schema:
                        yml_file.write(4 * " " + line)

                if res_schema:
                    yml_file.write("    response_schema: \n")
                    for line in api.res_schema:
                        yml_file.write(4 * " " + line)

                yml_file.write("    defined_data_list: []\n\n")

    @classmethod
    def get_api_list(cls, pb):
        api_list = []

        rpc_prefix = "rpc "
        http_method_list = ["get", "post", "delete", "put"]
        line = " test"

        # 找到service开头的部分
        while line:
            line = pb.readline()
            if line.startswith("service "):
                # print(line)
                break

        while line:
            line = pb.readline()
            strip_line = line.strip()

            # ignore empty line
            if len(strip_line) == 0:
                continue

            # 每个接口以 "rcp " 开头 如： rpc Verify(VerifyRequest) returns (VerifyResponse)
            if strip_line.startswith(rpc_prefix):
                api_struct = ApiStruct()
                api_struct.name = strip_line[len(rpc_prefix): strip_line.index("(")]
                api_struct.req_class = strip_line[strip_line.index("(") + 1:strip_line.index(")")]
                api_struct.res_class = strip_line[strip_line.rindex("(") + 1:strip_line.rindex(")")]

                while not strip_line.endswith("}"):
                    strip_line = pb.readline().strip()
                    for method in http_method_list:
                        if -1 != strip_line.find(method + ":"):
                            api_struct.uri = strip_line.split(":")[1].replace("\n", "").replace("\"", "")
                            api_struct.method = method.upper()
                            api_list.append(api_struct)
                print(api_struct)

        if not len(api_list) > 0:
            print("No api is found in pb")

        return api_list

    @classmethod
    def get_blob_list(cls, pb_content):
        # get first level blob(message/enum)
        blob_list = []
        index = 0
        length = len(pb_content)

        # separate pb into blobs by keywords enum/message
        while index < length:
            line = str(pb_content[index]).lstrip()
            index += 1

            if not line.startswith("enum ") and not line.startswith("message "):
                continue

            blob_content = []
            flag_tag_count = 0
            blob_end_found = False

            # find last line of blob
            while index < length and not blob_end_found:

                # ignore empty line
                if len(line) > 1 and not line.strip().startswith("//"):
                    blob_content.append(line)

                if line.endswith("{\n"):
                    flag_tag_count += 1

                if line.endswith("}\n"):
                    flag_tag_count -= 1

                if flag_tag_count == 0:
                    blob_end_found = True

                if not blob_end_found:
                    line = pb_content[index].lstrip()
                    index += 1

            # add blob to blob_list
            blob_list.append(blob_content)
        return blob_list

    @classmethod
    def get_class_blob_from_pb(cls, pb_blob):
        blob_list = cls.get_blob_list(pb_blob)

        class_dict = {}

        for blob in blob_list:
            cls.analyze_pb_content(blob, class_dict)

        return class_dict

    @classmethod
    def analyze_pb_content(cls, pb_content, class_dict):
        """
        support analyzing embedded message
        extract class from pb and save to class_dict
        pb_content must be an intact pb blob: such as
            message MapConfig {
                    int32 size = 1;
                    }
        """
        line = str(pb_content[0]).lstrip()

        if line.startswith("oneof "):
            # print("oneof key word is found : " + line)
            line = line.replace("oneof ", "message RENAME_IT_")

        if not line.startswith("enum ") and not line.startswith("message "):
            raise Exception("Not a valid class blob, first line is " + line)

        key = line.strip().split(" ")[1]
        class_dict[key] = [line]

        length = len(pb_content)
        flag_tag_count = 0
        blob_end_found = False
        line = str(pb_content[1]).lstrip()

        index = 1
        flag_tag_count += 1

        # find last line of blob
        while not blob_end_found and index < length:
            if line.startswith("enum ") or line.startswith("message ") or line.startswith("oneof "):
                skip_index = cls.analyze_pb_content(pb_content[index:], class_dict)
                index += skip_index + 1
                # if not line.startswith("oneof "):
                #     print("embedded class : " + str(index) + " : " + line)
                line = pb_content[index].lstrip()
                continue

            if len(line) > 1:  # ignore empty line which contain only "\n" or "":
                class_dict[key].append(line)

            if line.endswith("{\n"):
                flag_tag_count += 1

            if line.endswith("}\n"):
                flag_tag_count -= 1

            if flag_tag_count == 0:
                blob_end_found = True
                break

            if not blob_end_found:
                index += 1
                if index < length:
                    line = pb_content[index].lstrip()

        return index


class Swagger2Yaml:
    @classmethod
    def swagger_2_yaml(cls, swagger_file):
        if not os.path.isfile(swagger_file) or not swagger_file.endswith(".json"):
            print("Invalid file " + str(swagger_file))

        print("Converting swagger json file to yaml file: " + swagger_file)
        with open(swagger_file, "r", encoding='utf-8') as pb:
            swagger_content = json.load(pb)

        url_list = []
        api_struct_list = []
        def_cls_dict = {}
        for url in swagger_content['paths']:
            url_list.append(url)
            for method in swagger_content['paths'][url]:
                api_struct = ApiStruct()
                api_struct.uri = url
                api_struct.method = method
                api_struct.name = swagger_content['paths'][url][method]['summary']
                api_struct.req_class = swagger_content['paths'][url][method]['operationId'] + 'Request'
                api_struct.res_class = swagger_content['paths'][url][method]['operationId'] + 'Response'
                api_struct.req_schema = cls.get_req_schema(swagger_content['paths'][url][method]['parameters'],
                                                           api_struct.req_class)
                api_struct.res_schema = swagger_content['paths'][url][method]['responses']
                api_struct_list.append(api_struct)

        if "definitions" in swagger_content.keys():
            for key in swagger_content['definitions']:
                def_cls_dict[key] = swagger_content['definitions'][key]
                print(def_cls_dict[key])

        Pb2Yaml.generate_yml_file(api_struct_list, swagger_file, True, False)

    @classmethod
    def get_req_schema(cls, para_list, title):
        tab = " " * 4
        req_schema = [tab + "{\n", 2 * tab + "\"type\":\"object\",\n",
                      2 * tab + "\"title\": \"The " + title + "Schema\",\n"]
        properties = [2 * tab + "\"properties\": {\n"]
        required_list = []

        for para in para_list:

            if para["required"]:
                required_list.append(para['name'])

            if "type" in para.keys():
                properties.append(3 * tab + "\"" + para['name'] + "\": {\n")
                properties.append(4 * tab + "\"type\": \"" + para['type'] + "\",\n")
                if para['type'] == "array":
                    properties.append(5 * tab + "\"items\": [\n")
                    properties.append(5 * tab + "{\n")
                    properties.append(6 * tab + "\"type\": \"object\",\n")
                    properties.append(5 * tab + "},\n")
                    properties.append(4 * tab + "]\n")
                properties.append(3 * tab + "},\n")
            elif "schema" in para.keys():
                print(str(para))
                print("schema key world found in req")

        properties.append(2 * tab + "}\n")

        req_elem_val = 2 * tab + "\"required\": ["
        for required_elem in required_list:
            req_elem_val += "\"" + required_elem + "\","
        req_elem_val += "],\n"
        req_schema.append(req_elem_val)
        req_schema.extend(properties)
        req_schema.append(tab + "}\n")
        return req_schema

    @classmethod
    def get_res_schema(cls, para_list, title):
        pass


if __name__ == '__main__':
    file = "../server/server.proto"
    Pb2Yaml.pb2ymal(file, req_schema=False)

    # file = "../server/swagger.json"
    # Swagger2Yaml.swagger_2_yaml(file)
