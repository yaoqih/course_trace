# course_trace
Trace translate for huggingface couse

## Abstract

This repository leverages GitHub Actions to monitor another repository for changes in specific directories and files. This is particularly helpful for keeping translations up-to-date by tracking modifications to the source text and facilitating timely updates to the translated content.

## Useage

### 1. Fork this repo

You can use any name, but it's recommended to use the name of the repository you want to trace, followed by `_trace`.For example, I want to trace the `course` repository, so I'll name `courese_trace`

### 2. Eidt the `init_file.txt`

In this file, you need to record the warehouse to be tracked and the directory or file to be tracked.

The first line is the url of the repository to be traced, which is the source repository to be traced(upstream).

You can now add up to n lines to this file. On each line, enter a file or directory you want to track, followed by a `:`and the `commit_id` you want to start tracking from. If you leave out the `commit_id`, it will track from the latest commit.

For example:
```
https://github.com/huggingface/course
chapters/en:ffbbcc850e3398a5807240fd574ded9b5505e19b
```
This example indicates that we will be tracking changes to the files contained within the `chapters/en` folder of the Hugging Face course repository (`https://github.com/huggingface/course`). This tracking will begin with the version of the repository immediately following the commit identified by the hash `ffbbcc850e3398a5807240fd574ded9b5505e19b`.

The best part is that the file and path specifications support `.gitignore` syntax, making it a breeze to fill out. 

Don't remember to make a commit after you've finished filling in `init_file.txt`. 

### 3. Add your personal access tokens 

#### 3.1 Generate a Fine-grained Personal Access Token

Next, you need to create a personal access token (PAT) for this repository so the action can commit and create issues. I'll use `course_trace` as an example below. Replace it with your forked repo's name.

1. **Go to your GitHub Settings:**
    *   Click on your profile picture in the top right corner of GitHub.
    *   Select "Settings" from the dropdown menu.

2. **Navigate to Developer Settings:**
    *   In the left sidebar, scroll down and click on "Developer settings".

3. **Access Personal Access Tokens:**
    *   Click on "Personal access tokens".
    *   Choose "Fine-grained tokens"

4. **Generate a New Token:**
    *   Click on the "Generate new token" button.

5. **Configure Token Settings:**
    *   **Token name:** Give your token a descriptive name (e.g., "course\_trace\_access").
    *   **Expiration:** Select "No expiration" since you require permanent access.
    *   **Resource owner:** Make sure your user account is selected.
    *   **Repository access:** Choose "Only select repositories".
    *   **Selected repositories:** Search for and select your `course_trace` repository.

6. **Set Permissions:**
    *   Under "Repository permissions", find the following and set them to "Read and write":
        *   **Contents:**  (Repository contents, commits, branches, downloads, releases, and merges.)
        *   **Issues:** (Issues and related comments, assignees, labels, and milestones.)
    *   Leave all other permissions as "No access" unless you specifically need them.

7. **Generate Token:**
    *   Scroll to the bottom and click "Generate token".

8. **Copy Your Token:**
    *   **Important:** GitHub will only show you the token **once**. Copy it immediately and store it securely. You won't be able to see it again.

#### 3.2 Add the Token as a Repository Secret

1. **Go to Your Repository:**
    *   Navigate to your `course_trace` repository on GitHub.

2. **Access Repository Settings:**
    *   Click on the "Settings" tab in the repository's navigation bar.

3. **Navigate to Secrets:**
    *   In the left sidebar, under "Security", click on "Secrets and variables", then click on "Actions".

4. **Create a New Secret:**
    *   Click on the "New repository secret" button.

5. **Configure the Secret:**
    *   **Name:** Enter `TRACE_TOKEN` (Don't change, otherwise action can't find token).
    *   **Secret:** Paste the Fine-grained PAT you copied in 3.1.

6. **Add Secret:**
    *   Click the "Add secret" button.

**You're all set!**

### 4.Run the Init_tract acion


#### 4.1 1. Run Init Trace (Main Branch)

   This Action generates or updates a `trace_record.json` file, which likely contains some form of tracking or logging data.

   *   **Steps:**
       1. Navigate to your repository on GitHub.
       2. Make sure you are on the `main` branch.
       3. Click on the "Actions" tab.
       4. In the left sidebar, find the workflow named "Run Init Trace".
       5. Click on the "Run workflow" dropdown button on the right.
       6. Click the green "Run workflow" button to trigger it on the `main` branch.

   *   **Expected Outcome (Success):**
       *   The workflow will run successfully (indicated by a green checkmark).
       *   A new commit will be automatically added to the `main` branch.
       *   This commit will update the `trace_record.json` file in your repository.

   *   **Expected Outcome (Failure):**
       *   The workflow will fail (indicated by a red "X").
       *   No commit will be created.
       *   Click on the failed workflow run.
       *   Expand the different steps/jobs within the workflow to see the logs and error messages. These logs will provide information on why the workflow failed.

#### 4.2 (Optional) Run Monthly Trace

   This Action likely performs a comparison or analysis, potentially related to the data in `trace_record.json`, and reports any differences found.

   *   **Steps:**
       1. Go to the "Actions" tab in your repository.
       2. Find the workflow named "Monthly Trace" in the left sidebar.
       3. Click on the "Run workflow" dropdown on the right.
       4. Click the green "Run workflow" button.

   *   **Expected Outcome (Success, with differences):**
       *   The workflow will run successfully.
       *   A new issue will be automatically created in your repository. This issue will likely contain details about the differences (diff) that were detected.

   *   **Expected Outcome (Success, no differences):**
       *   The workflow will run successfully.
       *   No issue will be created.
       *   The workflow logs will contain the output "No diff", indicating that no significant changes were found.

This repository will automatically run the `Monthly Trace` workflow every month. If you want to change the frequency of this run, you can edit the `.github/workflows/trace.yml` file.

Eojoy it!
