// Copyright (c) Juelich Supercomputing Centre (JSC)
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel, DOMWidgetView, ISerializers
} from '@jupyter-widgets/base';

import {
  MODULE_NAME, MODULE_VERSION
} from './version';

import * as _ from 'lodash';
import { parseDicom } from 'dicom-parser';
import { clone } from 'underscore';

import CryptoJS = require('crypto-js');
import SparkMD5 = require('spark-md5');

export
class UploaderModel extends DOMWidgetModel {
  defaults() {
    return {...super.defaults(),
      _model_name: UploaderModel.model_name,
      _model_module: UploaderModel.model_module,
      _model_module_version: UploaderModel.model_module_version,
      _view_name: UploaderModel.view_name,
      _view_module: UploaderModel.view_module,
      _view_module_version: UploaderModel.view_module_version,

      accept: '',
      description: 'Upload',
      tooltip: '',
      disabled: false,
      icon: 'upload',
      button_style: '',
      multiple: false,
      metadata: [],
      style: null,

      token:'',
      upload_url: 'http://localhost:8888/api/contents/',
      _upload: false,
      hash: '',
      files: [],
      responses: [],
      finished: false,
    };
  }

  static serializers: ISerializers = {
      ...DOMWidgetModel.serializers,
    }

  static model_name = 'UploaderModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'UploaderView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}


export
class UploaderView extends DOMWidgetView {

  el: HTMLButtonElement;
  fileInput: HTMLInputElement;

  render() {
    super.render();

    this.el.classList.add('jupyter-widgets');
    this.el.classList.add('widget-upload');
    this.el.classList.add('jupyter-button');

    this.fileInput = document.createElement('input');
    this.fileInput.type = 'file';
    this.fileInput.style.display = 'none';
    this.el.appendChild(this.fileInput);

    this.el.addEventListener('click', () => {
      this.fileInput.click();
    });

    this.fileInput.addEventListener('click', () => {
      this.fileInput.value = '';
    });

    this.fileInput.addEventListener('change', () => {
      // Reset upload to `false` when new files are selected.
      this.model.set('_upload', false);
      this.model.set('finished', false);
      this.model.set('hash', '');

      let fileList = Array.from(this.fileInput.files)
      this.model.set({
        'fileList': fileList
      });

      let files = [];
      let responses = [];
      fileList.forEach(file => {
        files.push(file.name);
        responses.push(null);
      });
      this.model.set({
        'files': files
      });
      this.model.set({
        'responses': responses
      });
      this.touch();
    });

    this.model.on('change:_upload', this.upload_files, this);
    this.model.on('change:files', this.create_hash, this);

    this.listenTo(this.model, 'change:button_style', this.update_button_style);
    this.set_button_style();
    this.update();
  }

  update() {
    this.el.disabled = this.model.get('disabled');
    this.el.setAttribute('title', this.model.get('tooltip'));

    let description = `${this.model.get('description')}`
    let icon = this.model.get('icon');
    if (description.length || icon.length) {
        this.el.textContent = '';
        if (icon.length) {
            let i = document.createElement('i');
            i.classList.add('fa');
            i.classList.add('fa-' + icon);
            if (description.length === 0) {
                i.classList.add('center');
            }
            this.el.appendChild(i);
        }
        this.el.appendChild(document.createTextNode(description));
    }

    this.fileInput.accept = this.model.get('accept');
    this.fileInput.multiple = this.model.get('multiple');

    return super.update();
  }

  update_button_style() {
    this.update_mapped_classes(UploaderView.class_map, 'button_style', this.el);
  }

  set_button_style() {
      this.set_mapped_classes(UploaderView.class_map, 'button_style', this.el);
  }

  create_hash() {
    let fileList = this.model.get('fileList');
    let hashList = Array(fileList.length);
    
    let that = this;

    fileList.forEach(function (file, index) {
      let reader = new FileReader();
      reader.onloadend = function(evt) {
        hashList[index] = SparkMD5.ArrayBuffer.hash(reader.result);
        if (index == fileList.length - 1) {
          let spark = new SparkMD5();
          hashList.forEach(function (hash) {
            spark.append(hash);
          })
          let hexHash = spark.end();
          console.log(hexHash);
          that.model.set({
            'hash': hexHash,
          });
          that.touch();
        }
      }
      reader.readAsArrayBuffer(file);
    })
  }

  upload_files() {
    if (this.model.get('_upload') == false) { return; }

    let token = "token " + this.model.get('token');
    let upload_url = this.model.get('upload_url');
    let that = this;

    function parseFile(file, index) {

      function Uint8ToBase64(u8Arr){
        let CHUNK_SIZE = 0x8000; //arbitrary number
        let index = 0;
        let length = u8Arr.length;
        let result = '';
        while (index < length) {
          let slice = u8Arr.subarray(index, Math.min(index + CHUNK_SIZE, length)); 
          result += String.fromCharCode.apply(null, slice);
          index += CHUNK_SIZE;
        }
        return btoa(result);
      }

      function removeHeader(arrayBuffer) {
        let byteArray = new Uint8Array(arrayBuffer);
        // Parse the arrayBuffer. Return null if the file is not a DICOM file.
        try {
          var dataSet = parseDicom(byteArray);
        }
        catch (e) {
          return null;
        }

        // Slice the byteArray and remove elements of group 0008 and 0010
        let tags = Object.keys(dataSet.elements);
        let group8_first_tag = _.find(tags, (t) => {
          return t.startsWith('x0008');
        });
        let group8_offset = dataSet.elements[group8_first_tag].dataOffset - 8;
        let group10_last_tag = _.findLast(tags, (t) => {
          return t.startsWith('x0010');
        });
        let group10_offset = dataSet.elements[group10_last_tag].dataOffset
          + dataSet.elements[group10_last_tag].length;

        let slice1 = byteArray.slice(0, group8_offset);
        let slice2 = byteArray.slice(group10_offset);

        // Create a new Uint8 array with the sliced parts of the original array.
        let slicedByteArray = new Uint8Array(slice1.length + slice2.length);
        slicedByteArray.set(slice1);
        slicedByteArray.set(slice2, slice1.length);
        return slicedByteArray;
      }

      let readEventHandler = function (evt) {
        if (evt.target.error == null) {
          let slicedByteArray = removeHeader(evt.target.result);
          if (slicedByteArray == null) {
            let responses = clone(that.model.get('responses'));
            responses[index] = 'Not a dicom file';
            that.model.set('responses', responses)

            if (index == fileList.length - 1) {
              that.model.set('finished', true);
            }
            that.touch();
            return;
          }
          let b64String = Uint8ToBase64(slicedByteArray);

          let model = { name: file.name, path: file.name }
          model["type"] = 'file';
          model["format"] = 'base64';
          if (that.model.get('password') == null) {
            model["content"] = b64String;
          } else { // Encrypt
            let key = that.model.get('password');
            model["content"] = CryptoJS.AES.encrypt(b64String, key).toString();
          }

          fetch(upload_url + file.name, {
            method: "PUT",
            headers: {
              "Authorization": token,
              "Content-Type": "application/json",
            },
            body: JSON.stringify(model),
          })
          .then(function (response) {
            if (!response.ok) {
              throw response
            }
            return response.json()
          })
          .then(function (myJson) {
            console.log(JSON.stringify(myJson));

            let responses = clone(that.model.get('responses'));
            responses[index] = 'ok';
            that.model.set('responses', responses)

            if (index == fileList.length - 1) {
              that.model.set('finished', true);
            }
            that.touch()
            return;
          })
          .catch(function (err) {
            console.log(err);

            let responses = clone(that.model.get('responses'));
            responses[index] = err.status + ' ' + err.statusText;
            that.model.set('responses', responses)

            if (index == fileList.length - 1) {
              that.model.set('finished', true);
            } 
            that.touch();
          })

        } else {
          console.log("Read error: " + evt.target.error);
          return;
        }
      }

      let reader = new FileReader();
      reader.onload = readEventHandler;
      reader.readAsArrayBuffer(file);

    } 
    
    let fileList = this.model.get('fileList');
    fileList.forEach(function (file, index) {
      parseFile(file, index);
    }); 
  }

  static class_map = {
      primary: ['mod-primary'],
      success: ['mod-success'],
      info: ['mod-info'],
      warning: ['mod-warning'],
      danger: ['mod-danger']
  };
}
