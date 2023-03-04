import os
# pip install PyGithub
from github import Github


def 版本号格式加一(版本号):
    版本号 = 版本号.split('.')
    版本号[-1] = str(int(版本号[-1]) + 1)
    版本号 = '.'.join(版本号)
    return 版本号


def 版本号从大小写排序(tags):
    # 删除非数字的版本号
    tags = [tag for tag in tags if tag.replace('.', '').isdigit()]
    tags_dict = []
    for tag in tags:
        # 获取数值
        tag_value = int("".join(tag.split('.')))
        tags_dict.append({
            "tag": tag,
            'tagint': tag_value
        })
    tags_dict.sort(key=lambda student: student['tagint'])
    tags_dict.reverse()
    # 重新组装
    tags = []
    for tag in tags_dict:
        tags.append(tag['tag'])
    return tags


def 创建版本并上传构件(token, project_name, 上传文件列表=[], 标题="", 发布内容=""):
    g = Github(token)
    # print("用户名",g.get_user().name)
    repo = g.get_repo(project_name)
    # print("项目名称",repo.name)
    print("标签数量", repo.get_tags().totalCount)
    if repo.get_tags().totalCount == 0:
        # 没有标签的话 创建标签 0.0.1
        sha = repo.get_commits()[0].sha
        新版本号 = "0.0.1"
        repo.create_git_ref(f"refs/tags/{新版本号}", sha)
        return 新版本号

    # 版本号对比
    tags = []
    k = 0
    for tag in repo.get_tags():
        print(tag.name)
        tags.append(tag.name)
        k += 1
        if k == 5:
            break  # 取前5个标签
    print("原来的 tags", tags)

    # 版本号排序
    tags = 版本号从大小写排序(tags)
    # print("版本号排序:", tags)
    新版本号 = 版本号格式加一(tags[0])
    # print("新版本号:", 新版本号)
    print("创建新版本", 新版本号)
    sha = repo.get_commits()[0].sha
    repo.create_git_ref(f"refs/tags/{新版本号}", sha)

    release = repo.create_git_release(
        tag=新版本号,
        name=标题 + 新版本号,
        message=发布内容,
        draft=False,
        prerelease=False
    )
    print("上传文件列表", 上传文件列表)

    # 循环上传文件列表
    for 上传文件 in 上传文件列表:
        print("上传文件", 上传文件, "文件是否存在", os.path.exists(上传文件))
        上传文件 = os.path.abspath(上传文件)
        print("上传文件 绝对路径", 上传文件, os.path.exists(上传文件))
        if 上传文件 == "":
            continue
        if not os.path.exists(上传文件):
            print("文件不存在", 上传文件)
            continue
        文件名 = os.path.basename(上传文件)

        release.upload_asset(
            content_type='application/octet-stream',
            name=文件名,
            path=上传文件
        )

    return 新版本号


import glob


def 搜索目录下的文件多参数(搜索目录):
    # 搜索目录 window/*.exe,macos/*.zip
    search_directories = 搜索目录.split(',')
    print("搜索目录", search_directories)
    matched_files = []
    for directory in search_directories:
        files = glob.glob(directory)
        matched_files.extend(files)
    return matched_files


def main():
    YOUR_GITHUB_REPOSITORY = os.environ.get('YOUR_GITHUB_REPOSITORY')
    INPUT_TOKEN = os.environ.get('INPUT_TOKEN')
    UP_FILE_DIR = os.environ.get('UP_FILE_DIR')
    print(f"::set-output name=UP_FILE_DIR::{UP_FILE_DIR}")
    print(f"::set-output name=YOUR_GITHUB_REPOSITORY::{YOUR_GITHUB_REPOSITORY}")

    UPFILE_LIST = 搜索目录下的文件多参数(UP_FILE_DIR)
    print("搜索到的文件", UPFILE_LIST)

    新版本号 = 创建版本并上传构件(INPUT_TOKEN, YOUR_GITHUB_REPOSITORY, UPFILE_LIST, "", "更新内容")
    print(f"::set-output name=NewVersion::{新版本号}")


if __name__ == "__main__":
    main()
    # fileList = 搜索目录下的文件多参数("./window/*.exe,./macos/*.zip")
    # print(fileList)
