# Pupil Cloud API Client

Pupil Cloud API

- API version: 1.0
- Package version: 1.0.1

## Requirements.

Python 2.7 and 3.4+

## Installation & Usage

### Pip install

Install directly using:

```sh
pip install pupilcloud
```

or

```sh
pip install git+https://github.com/pupil-labs/pupil-cloud-client-python.git
```

(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/pupil-labs/pupil-cloud-client-python.git`)

Then import the package:

```python
import pupilcloud
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```

(or `sudo python setup.py install` to install the package for all users)

Then import the package:

```python
import pupilcloud
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python
from pupilcloud import Api, ApiException

api = pupilcloud.Api(api_key="API_KEY", host="https://api.cloud.pupil-labs.com")

try:
    # Returns the current logged in user based on auth token
    data = api.get_profile().result
    print(data)
except ApiException as e:
    print("Exception when calling AuthApi->get_profile: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to _https://api.cloud.pupil-labs.com_

| Class           | Method                                                                       | HTTP request                                        | Description                                            |
| --------------- | ---------------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------ |
| _AuthApi_       | [**get_profile**](docs/AuthApi.md#get_profile)                               | **GET** /auth/profile                               | Returns the current logged in user based on auth token |
| _LabelsApi_     | [**delete_label**](docs/LabelsApi.md#delete_label)                           | **DELETE** /labels/{label_id}                       | Delete a label                                         |
| _LabelsApi_     | [**get_label**](docs/LabelsApi.md#get_label)                                 | **GET** /labels/{label_id}                          | Returns a label with {label_id}                        |
| _LabelsApi_     | [**get_labels**](docs/LabelsApi.md#get_labels)                               | **GET** /labels/                                    | List all labels                                        |
| _LabelsApi_     | [**patch_label**](docs/LabelsApi.md#patch_label)                             | **PATCH** /labels/{label_id}                        | Update a label                                         |
| _LabelsApi_     | [**post_label**](docs/LabelsApi.md#post_label)                               | **POST** /labels/                                   | Create a new label                                     |
| _RecordingsApi_ | [**delete_recording**](docs/RecordingsApi.md#delete_recording)               | **DELETE** /recordings/{recording_id}               | Delete a recording                                     |
| _RecordingsApi_ | [**download_recording_file**](docs/RecordingsApi.md#download_recording_file) | **GET** /recordings/{recording_id}/files/{filename} | Download a recording&#39;s file                        |
| _RecordingsApi_ | [**download_recording_zip**](docs/RecordingsApi.md#download_recording_zip)   | **GET** /recordings/{recording_id}.zip              | Download recording files as a zip file                 |
| _RecordingsApi_ | [**download_recordings_zip**](docs/RecordingsApi.md#download_recordings_zip) | **GET** /recordings.zip                             | Download multiple recordings in zip archive            |
| _RecordingsApi_ | [**get_recording**](docs/RecordingsApi.md#get_recording)                     | **GET** /recordings/{recording_id}                  | Returns a recording with {recording_id}                |
| _RecordingsApi_ | [**get_recording_events**](docs/RecordingsApi.md#get_recording_events)       | **GET** /recordings/{recording_id}/events           | List recording events                                  |
| _RecordingsApi_ | [**get_recording_files**](docs/RecordingsApi.md#get_recording_files)         | **GET** /recordings/{recording_id}/files            | List recording files                                   |
| _RecordingsApi_ | [**get_recordings**](docs/RecordingsApi.md#get_recordings)                   | **GET** /recordings/                                | List all recordings                                    |
| _RecordingsApi_ | [**patch_recording**](docs/RecordingsApi.md#patch_recording)                 | **PATCH** /recordings/{recording_id}                | Update a recording                                     |
| _TemplatesApi_  | [**delete_template**](docs/TemplatesApi.md#delete_template)                  | **DELETE** /templates/{template_id}                 | Delete a template                                      |
| _TemplatesApi_  | [**get_template**](docs/TemplatesApi.md#get_template)                        | **GET** /templates/{template_id}                    | Returns a template with {template_id}                  |
| _TemplatesApi_  | [**get_templates**](docs/TemplatesApi.md#get_templates)                      | **GET** /templates/                                 | List all templates                                     |
| _TemplatesApi_  | [**patch_template**](docs/TemplatesApi.md#patch_template)                    | **PATCH** /templates/{template_id}                  | Update a template                                      |
| _TemplatesApi_  | [**post_template**](docs/TemplatesApi.md#post_template)                      | **POST** /templates/                                | Create a new template                                  |
| _WearersApi_    | [**delete_wearer**](docs/WearersApi.md#delete_wearer)                        | **DELETE** /wearers/{wearer_id}                     | Delete a wearer                                        |
| _WearersApi_    | [**get_wearer**](docs/WearersApi.md#get_wearer)                              | **GET** /wearers/{wearer_id}                        | Returns a wearer with {wearer_id}                      |
| _WearersApi_    | [**get_wearers**](docs/WearersApi.md#get_wearers)                            | **GET** /wearers/                                   | List all wearers                                       |
| _WearersApi_    | [**patch_wearer**](docs/WearersApi.md#patch_wearer)                          | **PATCH** /wearers/{wearer_id}                      | Update a wearer                                        |
| _WearersApi_    | [**post_wearer**](docs/WearersApi.md#post_wearer)                            | **POST** /wearers/                                  | Create a new wearer                                    |

## Documentation For Models

- [Label](docs/Label.md)
- [LabelGetResponse](docs/LabelGetResponse.md)
- [LabelPatchRequest](docs/LabelPatchRequest.md)
- [LabelPatchResponse](docs/LabelPatchResponse.md)
- [LabelPostRequest](docs/LabelPostRequest.md)
- [LabelPostResponse](docs/LabelPostResponse.md)
- [LabelsGetResponse](docs/LabelsGetResponse.md)
- [OffsetCorrection](docs/OffsetCorrection.md)
- [ProfileGetResponse](docs/ProfileGetResponse.md)
- [Recording](docs/Recording.md)
- [RecordingEvent](docs/RecordingEvent.md)
- [RecordingEventsGetResponse](docs/RecordingEventsGetResponse.md)
- [RecordingFile](docs/RecordingFile.md)
- [RecordingFilesGetResponse](docs/RecordingFilesGetResponse.md)
- [RecordingGetResponse](docs/RecordingGetResponse.md)
- [RecordingPatchRequest](docs/RecordingPatchRequest.md)
- [RecordingPatchResponse](docs/RecordingPatchResponse.md)
- [RecordingWithFiles](docs/RecordingWithFiles.md)
- [RecordingsGetResponse](docs/RecordingsGetResponse.md)
- [Template](docs/Template.md)
- [TemplateDeleteResponse](docs/TemplateDeleteResponse.md)
- [TemplateGetResponse](docs/TemplateGetResponse.md)
- [TemplateItem](docs/TemplateItem.md)
- [TemplatePatchRequest](docs/TemplatePatchRequest.md)
- [TemplatePatchResponse](docs/TemplatePatchResponse.md)
- [TemplatePostRequest](docs/TemplatePostRequest.md)
- [TemplatePostResponse](docs/TemplatePostResponse.md)
- [TemplatesGetResponse](docs/TemplatesGetResponse.md)
- [User](docs/User.md)
- [Wearer](docs/Wearer.md)
- [WearerDeleteResponse](docs/WearerDeleteResponse.md)
- [WearerGetResponse](docs/WearerGetResponse.md)
- [WearerPatchRequest](docs/WearerPatchRequest.md)
- [WearerPatchResponse](docs/WearerPatchResponse.md)
- [WearerPostRequest](docs/WearerPostRequest.md)
- [WearerPostResponse](docs/WearerPostResponse.md)
- [WearersGetResponse](docs/WearersGetResponse.md)

## Documentation For Authorization

## api_key

- **Type**: API key
- **API key parameter name**: api-key
- **Location**: HTTP header

## Author
