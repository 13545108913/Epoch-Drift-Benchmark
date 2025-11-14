# -*- coding: utf-8 -*-

import gitlab
import subprocess
import os
import shutil
from urllib.parse import urlparse

# --- 1. 配置变量 (请务必修改!) ---

# 您的 GitLab v12 实例的 URL
GITLAB_URL = 'http://localhost:8023' 

# 您在 GitLab v12 实例中创建的管理员访问令牌 (具有 api 和 sudo 权限)
GITLAB_ADMIN_TOKEN = 'm7h4MN8KxzWmg9qMpWmi' 

# 用于创建用户的默认密码
DEFAULT_USER_PASSWORD = 'a_very_strong_default_password_123!'

# Gitlab 管理员用户名 (通常是 'root')
GITLAB_ADMIN_USER = 'root' 

# --- 2. 模拟数据 (请替换为您自己的数据) ---
# 在实际使用中，您将用“阶段二”采样的1000+个用户名替换此列表
# 注意：用户名在 GitLab 中不能包含空格或特殊字符
USERNAMES_TO_CREATE = [
    'user_project_alpha',
    'jane_doe_dev',
    'test_user_001',
    'contributor_x',
    'another_user'
]

# 在实际使用中，您将用“阶段二”采样的300个仓库替换此列表
# 格式：{'name': '仓库名称', 'clone_url': '源仓库的 HTTPS .git URL'}
REPOS_TO_MIGRATE = [
    {
        'name': 'sample-repo-1', 
        'clone_url': 'https://github.com/git-fixtures/basic.git'
    },
    {
        'name': 'sample-repo-2-tags', 
        'clone_url': 'https://github.com/git-fixtures/tags.git'
    },
    {
        'name': 'sample-repo-3-branches', 
        'clone_url': 'https://github.com/git-fixtures/branches.git'
    }
]
# ----------------------------------------------------


def create_gitlab_users(gl_instance, usernames):
    """
    在 GitLab 实例中批量创建用户。
    """
    print(f"--- 开始创建 {len(usernames)} 个用户 ---")
    created_users = {}
    
    for username in usernames:
        # GitLab 需要一个唯一的电子邮件地址
        email = f"{username}@example.com" 
        
        try:
            user = gl_instance.users.create({
                'email': email,
                'username': username,
                'name': username.replace('_', ' ').title(), # 自动生成一个名字
                'password': DEFAULT_USER_PASSWORD,
                'skip_confirmation': True # 作为管理员，自动确认用户
            })
            created_users[username] = user
            print(f"[成功] 创建用户: {username} (ID: {user.id})")
            
        except gitlab.exceptions.GitlabCreateError as e:
            if "has already been taken" in str(e):
                print(f"[跳过] 用户名或邮箱 '{username}' 已存在。")
            else:
                print(f"[失败] 创建用户 {username} 失败: {e}")
        except Exception as e:
            print(f"[严重失败] 创建用户 {username} 时发生未知错误: {e}")
            
    print(f"--- 用户创建完成 --- \n")
    return created_users

def migrate_git_repos(gl_instance, repos):
    """
    将 Git 仓库（包括代码、分支、标签）迁移到 GitLab 实例。
    """
    print(f"--- 开始迁移 {len(repos)} 个仓库 ---")
    
    # 从 GitLab URL 中提取主机名 (例如 localhost:8023)
    parsed_url = urlparse(GITLAB_URL)
    gitlab_host = parsed_url.netloc # 例如 'localhost:8023'

    for repo in repos:
        repo_name = repo['name']
        source_clone_url = repo['clone_url']
        local_bare_repo_dir = f"{repo_name}.git"

        print(f"\n--- 正在处理仓库: {repo_name} ---")
        
        # 1. 在 GitLab 中创建项目
        try:
            # 默认将项目创建在管理员命名空间下
            project = gl_instance.projects.create({
                'name': repo_name,
                'visibility': 'public' # 您可以改为 'internal' 或 'private'
            })
            print(f"[1/4] 在 GitLab 中创建项目: {project.web_url}")
        
        except gitlab.exceptions.GitlabCreateError as e:
            if "has already been taken" in str(e):
                print(f"[1/4] 项目 '{repo_name}' 已存在，将尝试推送更新...")
                # 尝试查找现有项目
                try:
                    project = gl_instance.projects.get(f"{GITLAB_ADMIN_USER}/{repo_name}")
                except Exception as get_e:
                     print(f"[失败] 无法在 GitLab 中创建或找到项目 {repo_name}: {get_e}")
                     continue
            else:
                print(f"[失败] 无法在 GitLab 中创建项目 {repo_name}: {e}")
                continue
        except Exception as e:
             print(f"[失败] 无法在 GitLab 中创建项目 {repo_name}: {e}")
             continue

        # 2. 构建包含认证信息的 GitLab 推送 URL
        # 格式: http://[用户名]:[令牌]@[主机名]/[项目路径].git
        gitlab_push_url = f"http://{GITLAB_ADMIN_USER}:{GITLAB_ADMIN_TOKEN}@{gitlab_host}/{project.path_with_namespace}.git"
        
        # 3. Git 操作：裸克隆 (Bare Clone)
        try:
            # 如果本地目录已存在，先删除
            if os.path.exists(local_bare_repo_dir):
                print(f"[2/4] 清理旧的本地裸仓库: {local_bare_repo_dir}")
                shutil.rmtree(local_bare_repo_dir)

            print(f"[2/4] 从 {source_clone_url} 裸克隆...")
            # --bare 创建一个没有工作目录的裸仓库
            subprocess.run(
                ['git', 'clone', '--bare', source_clone_url, local_bare_repo_dir], 
                check=True, capture_output=True, text=True
            )
            print(f"[2/4] 裸克隆完成。")

        except subprocess.CalledProcessError as e:
            print(f"[失败] 裸克隆 {source_clone_url} 失败: {e.stderr}")
            continue # 跳到下一个仓库

        # 4. Git 操作：镜像推送 (Mirror Push)
        try:
            print(f"[3/4] 正在将所有数据 (分支, 标签) 镜像推送到 GitLab...")
            # -C [目录] : 在该目录中执行 git 命令
            # --mirror : 推送所有引用 (refs), 包括所有分支和标签
            subprocess.run(
                ['git', '-C', local_bare_repo_dir, 'push', '--mirror', gitlab_push_url],
                check=True, capture_output=True, text=True
            )
            print(f"[3/4] 镜像推送成功！")
        
        except subprocess.CalledProcessError as e:
            print(f"[失败] 镜像推送到 {repo_name} 失败: {e.stderr}")
            # 即使推送失败，也继续执行清理
        
        # 5. 清理本地的裸仓库
        try:
            print(f"[4/4] 清理本地裸仓库: {local_bare_repo_dir}")
            shutil.rmtree(local_bare_repo_dir)
            print(f"[成功] 仓库 {repo_name} 迁移完成。")
        except OSError as e:
            print(f"[警告] 清理本地目录 {local_bare_repo_dir} 失败: {e}")

    print(f"\n--- 所有仓库迁移完成 ---")


def main():
    """
    主执行函数
    """
    print(f"正在连接到 GitLab 实例: {GITLAB_URL} ...")
    
    try:
        # 认证 GitLab 实例
        gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_ADMIN_TOKEN)
        # 尝试验证身份
        gl.auth() 
        print(f"成功连接！以管理员 '{gl.user.username}' 身份登录。")
        print("----------------------------------------")
    
    except gitlab.exceptions.GitlabAuthenticationError:
        print(f"[严重错误] 认证失败！请检查您的 GITLAB_URL 和 GITLAB_ADMIN_TOKEN。")
        return
    except Exception as e:
        print(f"[严重错误] 连接到 {GITLAB_URL} 失败: {e}")
        return
    
    # 执行用户创建
    create_gitlab_users(gl, USERNAMES_TO_CREATE)
    
    # 执行仓库迁移
    migrate_git_repos(gl, REPOS_TO_MIGRATE)
    
    print("\n--- 脚本执行完毕 ---")

if __name__ == "__main__":
    main()