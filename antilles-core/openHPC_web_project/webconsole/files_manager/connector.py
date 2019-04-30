# -*- coding: utf-8 -*-

"""
Copyright © 2019-present Lenovo

This file is licensed under both the BSD-3 license for individual/non-commercial use and
EPL-1.0 license for commercial use. Full text of both licenses can be found in
COPYING.BSD and COPYING.EPL files.
"""

import base64
import logging
import mimetypes
import os
import os.path
import pwd
import re
import shutil
import stat
import tarfile
import time
import zipfile
from datetime import datetime

from django.http import StreamingHttpResponse
from six import raise_from

from antilles.common.exceptions import AntillesBaseException

logger = logging.getLogger(__name__)


class FilesConnector(object):
    ERROR_UNKNOWN           = 'errUnknown'
    ERROR_UNKNOWN_CMD       = 'errUnknownCmd'
    ERROR_CONF              = 'errConf'
    ERROR_CONF_NO_JSON      = 'errJSON'
    ERROR_CONF_NO_VOL       = 'errNoVolumes'
    ERROR_INV_PARAMS        = 'errCmdParams'
    ERROR_OPEN              = 'errOpen'
    ERROR_DIR_NOT_FOUND     = 'errFolderNotFound'
    ERROR_FILE_NOT_FOUND    = 'errFileNotFound'
    ERROR_TRGDIR_NOT_FOUND  = 'errTrgFolderNotFound'
    ERROR_NOT_DIR           = 'errNotFolder'
    ERROR_NOT_FILE          = 'errNotFile'
    ERROR_PERM_DENIED       = 'errPerm'
    ERROR_LOCKED            = 'errLocked'
    ERROR_EXISTS            = 'errExists'
    ERROR_INVALID_NAME      = 'errInvName'
    ERROR_MKDIR             = 'errMkdir'
    ERROR_MKFILE            = 'errMkfile'
    ERROR_RENAME            = 'errRename'
    ERROR_COPY              = 'errCopy'
    ERROR_MOVE              = 'errMove'
    ERROR_COPY_FROM         = 'errCopyFrom'
    ERROR_COPY_TO           = 'errCopyTo'
    ERROR_COPY_ITSELF       = 'errCopyInItself'
    ERROR_REPLACE           = 'errReplace'
    ERROR_RM                = 'errRm'
    ERROR_RM_SRC            = 'errRmSrc'
    ERROR_UPLOAD            = 'errUpload'
    ERROR_UPLOAD_FILE       = 'errUploadFile'
    ERROR_UPLOAD_NO_FILES   = 'errUploadNoFiles'
    ERROR_UPLOAD_TOTAL_SIZE = 'errUploadTotalSize'
    ERROR_UPLOAD_FILE_SIZE  = 'errUploadFileSize'
    ERROR_UPLOAD_FILE_MIME  = 'errUploadMime'
    ERROR_UPLOAD_TRANSFER   = 'errUploadTransfer'
    ERROR_NOT_REPLACE       = 'errNotReplace'
    ERROR_SAVE              = 'errSave'
    ERROR_EXTRACT           = 'errExtract'
    ERROR_ARCHIVE           = 'errArchive'
    ERROR_NOT_ARCHIVE       = 'errNoArchive'
    ERROR_ARCHIVE_TYPE      = 'errArcType'
    ERROR_EXTRACT_TYPE      = 'errExtType'
    ERROR_ARC_SYMLINKS      = 'errArcSymlinks'
    ERROR_ARC_MAXSIZE       = 'errArcMaxSize'
    ERROR_RESIZE            = 'errResize'
    ERROR_UNSUPPORT_TYPE    = 'errUsupportType'
    ERROR_NOT_UTF8_CONTENT  = 'errNotUTF8Content'
    ERROR_NETMOUNT          = 'errNetMount'
    ERROR_NETMOUNT_NO_DRIVER= 'errNetMountNoDriver'
    ERROR_NETMOUNT_FAILED   = 'errNetMountFailed'
    ERROR_SESSION_EXPIRES   = 'errSessionExpires'
    ERROR_CREATING_TEMP_DIR = 'errCreatingTempDir'
    ERROR_FTP_DOWNLOAD_FILE = 'errFtpDownloadFile'
    ERROR_FTP_UPLOAD_FILE   = 'errFtpUploadFile'
    ERROR_FTP_MKDIR         = 'errFtpMkdir'
    ERROR_ARCHIVE_EXEC      = 'errArchiveExec'
    ERROR_EXTRACT_EXEC      = 'errExtractExec'
    
    _options = {
        'volumeid': '11_',
        'root': '',
        'URL': '',
        'rootAlias': 'MyFolder',
        'dotFiles': False,
        'dirSize': False,
        'fileMode': 00755,
        'dirMode': 00755,
        'imgLib': 'auto',
        'tmbDir': '.tmb',
        'tmbAtOnce': 5,
        'tmbSize': 48,
        'fileURL': False,
        'uploadMaxSize': 10240,
        'uploadWriteChunk': 8192,
        'uploadAllow': [],
        'uploadDeny': [],
        'uploadOrder': ['deny', 'allow'],
        # 'aclObj': None, # TODO
        # 'aclRole': 'user', # TODO
        'defaults': {
            'read': 1,
            'write': 1,
            'rm': 1,
            'rename': 1
        },
        'perms': {},
        'archiveMimes': {},
        'archivers': {
            'create': {'application/zip': 'application/zip',
                        'application/x-tar': 'application/x-tar',
                        'application/x-gzip': 'application/x-gzip'},
            'extract': {'application/zip': 'application/zip',
                        'application/x-tar': 'application/x-tar',
                        'application/x-gzip': 'application/x-gzip'}
        },
        'disabled': [],
        'debug': False,
        'version': "2.0"
    }
    
    commands = {
        'open'     : {'target': False, 'tree': False, 'init': False, 'mimes': False},
        'ls'       : {'target': True, 'mimes': False},
        'tree'     : {'target': True},
        'parents'  : {'target': True},
        'tmb'      : {'targets': True},
        'file'     : {'target': True, 'download': False},
        'size'     : {'targets': True},
        'mkdir'    : {'target': True, 'name': True},
        'mkfile'   : {'target': True, 'name': True, 'mimes': False},
        'rm'       : {'targets': True},
        'rename'   : {'target': True, 'name': True, 'mimes': False},
        'duplicate': {'targets': True, 'suffix': False},
        'paste'    : {'targets': True, 'dst': True, 'cut': False, 'mimes': False},
        'upload'   : {'target': True, 'FILES': True, 'mimes': False, 'html': False},
        'get'      : {'target': True},
        'put'      : {'target': True, 'content': True, 'mimes': False},
        'archive'  : {'targets': True, 'type': True, 'mimes': False},
        'extract'  : {'target': True, 'mimes': False},
        'search'   : {'q': True, 'mimes': False},
        'info'     : {'targets': True},
        'hash'     : {'path': True},
        'dim'      : {'target': True},
        'preview'  : {'target': True},
        'resize'   : {'target': True, 'width': True, 'height': True, 'mode': False, 'x': False, 'y': False, 'degree': False},
        'netmount' : {'protocol': True, 'host': True, 'path': False, 'port': False, 'user': True, 'pass': True, 'alias': False, 'options': False}

        }
    
    _mimeType = {
        # text
        'txt': 'text/plain',
        'conf': 'text/plain',
        'ini': 'text/plain',
        'pbs': 'text/plain',
        'lsf': 'text/plain',
        'slurm': 'text/plain',
        'dat': 'text/plain',
        'data': 'text/plain',
        'xml': 'text/plain',
        'json': 'text/plain',
        'csv': 'text/plain',
        'yaml': 'text/plain',
        'md': 'text/plain',
        'prototxt': 'text/plain',
        'php': 'text/x-php',
        'html': 'text/html',
        'htm': 'text/html',
        'js' : 'text/javascript',
        'css': 'text/css',
        'rtf': 'text/rtf',
        'rtfd': 'text/rtfd',
        'py' : 'text/x-python',
        'java': 'text/x-java-source',
        'rb' : 'text/x-ruby',
        'sh' : 'text/x-shellscript',
        'pl' : 'text/x-perl',
        'sql': 'text/x-sql',
        # apps
        'doc': 'application/msword',
        'ogg': 'application/ogg',
        '7z': 'application/x-7z-compressed',
        'zip': 'application/zip',
        'tar': 'application/x-tar',
        'tar.gz': 'application/x-gzip',

    # video
        'ogm': 'appllication/ogm',
        'mkv': 'video/x-matroska'
    }

    def __init__(self, user):
        self.user = user
    
    def commandExists(self, cmd):
        if self.commands.has_key(cmd):
            try:
                return callable(getattr(self, cmd))
            except:
                return False
        else:
            return False
    
    def commandArgsList(self, cmd):
        return self.commands[cmd] if self.commandExists(cmd) else {};
    
    def error(self, *args):
        if len(args):
            return args
        else:
            return self.ERROR_UNKNOWN
    
    def execute(self, cmd, args):
        if not self.commandExists(cmd):
            return {'error': self.error(self.ERROR_UNKNOWN_CMD)}
        
        command = getattr(self, cmd)
        result = command(args)

        if isinstance(result, StreamingHttpResponse):
            return result

        # replace removed files info with removed files hashes
        if result.has_key('removed'):
            removed = []
            for file in result['removed']:
                if 'hash' in file:
                    removed.append(file['hash'])
                else:
                    removed.append(file)
            result['removed'] = list(set(removed))
            
        # remove hidden files and filter files by mimetypes
        if result.has_key('added'):
            result['added'] = self.filter(result['added'])
        
        # remove hidden files and filter files by mimetypes
        if result.has_key('changed'):
            result['changed'] = self.filter(result['changed'])
        
        return result
        
    def filter(self, files):
        for i in range(0, len(files)):
            file = files[i]
            if file.has_key('hidden'):
                del files[i]

        return files
    
    def __isAllowed(self, path, access):
        if not os.path.exists(path):
            return 0

        if access == 'read':
            if not self.is_readable(path):
                return 0
        elif access == 'write':
            if not self.is_writable(path):
                return 0
        elif access == 'rm' or access == 'rename':
            if not self.is_writable(os.path.dirname(path)):
                return 0
        else:
            return 0
        
        return self._options['defaults'][access]

    def is_readable(self, path):
        uid = self.user.uid
        gid = self.user.gid
        s = os.stat(path)
        mode = s[stat.ST_MODE]

        if stat.S_ISDIR(mode):
            if s[stat.ST_UID] == uid:
                return (mode & stat.S_IXUSR > 0) and (mode & stat.S_IRUSR > 0)
            elif s[stat.ST_GID] == gid:
                return (mode & stat.S_IXGRP > 0) and (mode & stat.S_IRGRP > 0)
            else:
                return (mode & stat.S_IXOTH > 0) and (mode & stat.S_IROTH > 0)
        else:
            if s[stat.ST_UID] == uid:
                return mode & stat.S_IRUSR > 0
            elif s[stat.ST_GID] == gid:
                return mode & stat.S_IRUSR > 0
            else:
                return mode & stat.S_IROTH > 0

    def is_writable(self, path):
        uid = self.user.uid
        gid = self.user.gid
        s = os.stat(path)
        mode = s[stat.ST_MODE]

        if stat.S_ISDIR(mode):
            if s[stat.ST_UID] == uid:
                return (mode & stat.S_IXUSR > 0) and (mode & stat.S_IWUSR > 0)
            elif s[stat.ST_GID] == gid:
                return (mode & stat.S_IXGRP > 0) and (mode & stat.S_IWGRP > 0)
            else:
                return (mode & stat.S_IXOTH > 0) and (mode & stat.S_IWOTH > 0)
        else:
            if s[stat.ST_UID] == uid:
                return mode & stat.S_IWUSR > 0
            elif s[stat.ST_GID] == gid:
                return mode & stat.S_IWUSR > 0
            else:
                return mode & stat.S_IWOTH > 0
    
    def __isAccepted(self, target):
        if target == '.' or target == '..':
            return False
        if target[0:1] == '.' and not self._options['dotFiles']:
            return False
        return True
    
    def __hash(self, path):
        """Hash of the path"""
        if isinstance(path, unicode):
            path = path.encode(encoding='utf-8', errors='ignore')
        _base64_str = base64.urlsafe_b64encode(path)
        #Because the front can not support hash with "%" and "=" can not appear in url, then remove "=".
        _base64_str = _base64_str.replace('=', '')
        base64_str = _base64_str.decode('utf-8')
        return base64_str
        # m = hashlib.md5()
        # m.update(path)
        # return str(m.hexdigest())

    def __dehash(self, hash):
        _hash = hash
        if isinstance(hash, unicode):
            _hash = hash.encode(encoding='utf-8', errors='ignore')
        # Recover "=" of base64 string

        try:
            fill_num = 4 - len(_hash) % 4
            base64_str = _hash + '=' * fill_num
            _de_base_str = base64.urlsafe_b64decode(base64_str)
            de_base_str = _de_base_str.decode('utf-8')

            return de_base_str
        except Exception as e:
            logger.exception(
                'dehash fail'
            )
            raise_from(
                AntillesBaseException('dehash fail'),
                e
            )

    def __findDir(self, fhash, path, tryFile=False):
        """Find directory by hash"""
        fhash = str(fhash)

        if fhash == self.__hash(path):
            return path

        if not os.path.isdir(path):
            return None

        target_path = self.__dehash(fhash)

        if not target_path.startswith(path):
            logger.warn('Unable to access: %s', target_path)
            raise AntillesBaseException('Can not access dir outside user workspace')

        if os.path.exists(target_path):
            return target_path

#         for d in os.listdir(path):
#             pd = os.path.join(path, d)
#             if tryFile and os.path.isfile(pd):
#                 if fhash == self.__hash(pd):
#                     return pd
# #             elif os.path.isdir(pd) and not os.path.islink(pd):
#             elif os.path.isdir(pd):
#                 if fhash == self.__hash(pd):
#                     return pd
#                 else:
#                     ret = self.__findDir(fhash, pd, True)
#                     if ret:
#                         return ret

        return None
    
    def __content(self, path, tree, rootPath):
        """CWD + CDC + maybe(TREE)"""
        cwd, options = self.__cwd(path, rootPath)
        dirs = self.__cdc(path, rootPath)
        
        if tree:
            hashs = {}
            for file in dirs:
                hashs[file['hash']] = file
            
            tree_dirs = self.__tree(rootPath, rootPath)['tree']
            for file in tree_dirs:
                if not file['hash'] in hashs:
                    hashs[file['hash']] = file
            dirs = hashs.values()
            
        return {
            'cwd': cwd,
            'options': options,
            'files': dirs
        }
    
    def __cwd(self, path, rootPath):
        """Current Working Directory"""
        name = os.path.basename(path)
        if path == rootPath:
            name = self._options['rootAlias']
            root = True
        else:
            root = False

        if self._options['rootAlias']:
            basename = self._options['rootAlias']
        else:
            basename = os.path.basename(rootPath)

        rel = basename + path[len(rootPath):]
        
        ts = os.stat(path).st_mtime
        cwd = {
            'mime': 'directory',
            'ts': int(ts),
            'read': self.__isAllowed(path, 'read'),
            'write': self.__isAllowed(path, 'write'),
            'size': 0,
            'hash': self.__hash(path),
            'name': self.__checkUtf8(name),
            'date': datetime.fromtimestamp(ts).strftime("%d %b %Y %H:%M"),
        }
        if root:
            cwd['volumeid'] = self._options['volumeid']
            cwd['locked'] = 1
        else:
            cwd['phash'] = self.__hash(os.path.dirname(path))
        
        for f in sorted(os.listdir(path)):
            if not self.__isAccepted(f): continue
            pf = os.path.join(path, f)
            if os.path.isdir(pf):
                cwd['dirs'] = 1
                break
        
        options = {
            'path': rel,
            'url': '',
            'tmbUrl': '',
            'disabled': self._options['disabled'],
            'separator': os.sep,
            'copyOverwrite': 1,
            'archivers': {
                'create': self._options['archivers']['create'].keys(),
                'extract': self._options['archivers']['extract'].keys()
            }
        }
        
        return (cwd, options)
    
    def __cdc(self, path, rootPath):
        """Current Directory Content"""
        files = []
        dirs = []

        for f in sorted(os.listdir(path)):
            if not self.__isAccepted(f): continue
            pf = os.path.join(path, f)
            info = {}
            info = self.__info(pf, rootPath)
            if info['mime'] == 'directory':
                dirs.append(info)
            else:
                files.append(info)
        
        dirs.extend(files)
        return dirs
    
    def __tree(self, path, rootPath, include_self=True):
        """Return directory tree starting from path"""

        if not os.path.isdir(path): return []
        
        tree = []
        if include_self:
            tree.append(self.__cwd(path, rootPath)[0])

        if self.__isAllowed(path, 'read'):
            for d in sorted(os.listdir(path)):
                pd = os.path.join(path, d)
                if os.path.isdir(pd) and self.__isAccepted(d):
                    pd_info = self.__cwd(pd, rootPath)[0]
                    pd_info['size'] = self.__dirSize(pd)
                    tree.append(pd_info)

        return {'tree': tree}
    
    def __parents(self, path, rootPath):
        """Return sub-tree to the current path, including current path"""

        if not os.path.isdir(path): return []
        if path == rootPath: 
            return {'tree': [self.__cwd(path, rootPath)[0]]}
        
        dirs = []
        while True:
            parent = os.path.dirname(path)
            if parent == rootPath:
                dirs.insert(0, self.__cwd(path, rootPath)[0])
                dirs.insert(0, self.__cwd(parent, rootPath)[0])
                break
            else:
                sub_dirs = self.__tree(parent, rootPath, False)['tree']
                dirs.extend(sub_dirs)
                path = parent

        return {'tree': dirs}
    
    def __info(self, path, rootPath):
        mime = ''
        filetype = 'file'
        if os.path.isfile(path): filetype = 'file'
        if os.path.isdir(path): filetype = 'dir'
#         if os.path.islink(path): filetype = 'link'
        
        stat = os.lstat(path)
        fdate = datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y %H:%M")
        info = {
            'mime': 'directory' if filetype == 'dir' else self.__mimetype(path),
            'ts': int(stat.st_mtime),
            'read': self.__isAllowed(path, 'read'),
            'write': self.__isAllowed(path, 'write'),
            'size': self.__dirSize(path) if filetype == 'dir' else stat.st_size,
            'hash': self.__hash(path),
            'name': self.__checkUtf8(os.path.basename(path)),
            'phash': self.__hash(os.path.dirname(path)),
            'date': fdate
        }

#         if filetype == 'link':
#             lpath = self.__readlink(path, rootPath)
#             if not lpath:
#                 info['mime'] = 'symlink-broken'
#                 return info
# 
#             if os.path.isdir(lpath):
#                 info['mime'] = 'directory'
#             else:
#                 info['mime'] = self.__mimetype(lpath)
#                 info['phash'] = self.__hash(os.path.dirname(lpath))
# 
#             if self._options['rootAlias']:
#                 basename = self._options['rootAlias']
#             else:
#                 basename = os.path.basename(rootPath)
# 
#             info['link'] = self.__hash(lpath)
#             info['linkTo'] = basename + lpath[len(rootPath):]
#             info['read'] = info['read'] and self.__isAllowed(lpath, 'read')
#             info['write'] = info['write'] and self.__isAllowed(lpath, 'write')
#         elif filetype == 'dir':
#        if filetype == 'dir':
#            for f in sorted(os.listdir(path)):
#                if not self.__isAccepted(f): continue
#                pf = os.path.join(path, f)
#                if os.path.isdir(pf):
#                    info['dirs'] = 1
#                    break
        
        return info
    
    def __mimetype(self, path):
        """Detect mimetype of file"""
        mime = mimetypes.guess_type(path)[0] or 'unknown'
        ext = path[path.rfind('.') + 1:]

        if mime == 'unknown' and ('.' + ext) in mimetypes.types_map:
            mime = mimetypes.types_map['.' + ext]

        if mime == 'text/plain' and ext == 'pl':
            mime = self._mimeType[ext]

        if mime == 'application/vnd.ms-office' and ext == 'doc':
            mime = self._mimeType[ext]

        if mime == 'unknown':
            if os.path.basename(path) in ['README', 'ChangeLog']:
                mime = 'text/plain'
            else:
                if ext in self._mimeType:
                    mime = self._mimeType[ext]
                else:
                    mime = 'text/plain'

        return mime
    
    def __dirSize(self, path, tryFile=False):
        if tryFile and os.path.isfile(path) and os.path.exists(path):
            return os.stat(path).st_size

        total_size = os.lstat(path).st_size
        return total_size
    
    def __readlink(self, path, rootPath):
        """Read link and return real path if not broken"""
        target = os.readlink(path);
        if not target[0] == '/':
            target = os.path.join(os.path.dirname(path), target)
        target = os.path.normpath(target)
        if os.path.exists(target):
            if not target.find(rootPath) == -1:
                return target
        return False
    
    def __runSubProcess(self, cmd, validReturn = [0]):
        if self._sp is None:
            import subprocess
            self._sp = subprocess

        try:
            sp = self._sp.Popen(cmd, shell = False, stdout = self._sp.PIPE, stderr = self._sp.PIPE, stdin = self._sp.PIPE)
            out, err = sp.communicate('')
            ret = sp.returncode
        except:
            return False

        if not ret in validReturn:
            return False

        return True

    def __checkUtf8(self, name):
        try:
            name.decode('utf-8')
        except UnicodeDecodeError:
            name = unicode(name, 'utf-8', 'replace')
        except UnicodeEncodeError:
            pass
        return name    
        
    def open(self, args):
        root = self.user.workspace
        init = args.has_key('init') and args['init'] == '1'
        path = ''
        
        if args['target']:
            target = self.__findDir(args['target'], root)
            if not target:
                return {'error': self.error(self.ERROR_INV_PARAMS)}
            elif not self.__isAllowed(target, 'read'):
                return {'error': self.error(self.ERROR_PERM_DENIED)}
            else:
                path = target
        else:
            path = root
                
        tree = args.has_key('tree') and args['tree'] == '1'
        result = self.__content(path, tree, root)
        
        if init:
            result['api'] = self._options['version']
            result['uplMaxSize'] = self._options['uploadMaxSize']
        
        return result
    
    def ls(self, args):
        pass
    
    def tree(self, args):
        root = self.user.workspace
        path = ''
        
        if args['target']:
            target = self.__findDir(args['target'], root)
            if not target:
                return {'error': self.error(self.ERROR_INV_PARAMS)}
            elif not self.__isAllowed(target, 'read'):
                return {'error': self.error(self.ERROR_PERM_DENIED)}
            else:
                path = target
        else:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        
        return self.__tree(path, root)
    
    def parents(self, args):
        root = self.user.workspace
        path = ''
        
        if args['target']:
            target = self.__findDir(args['target'], root)
            if not target:
                return {'error': self.error(self.ERROR_INV_PARAMS)}
            elif not self.__isAllowed(target, 'read'):
                return {'error': self.error(self.ERROR_PERM_DENIED)}
            else:
                path = target
        else:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        
        return self.__parents(path, root)
    
    def tmb(self, args):
        pass
    
    def size(self, args):
        root = self.user.workspace
        path = ''
        
        if args['targets']:
            size = 0
            for single in args['targets']:
                target = self.__findDir(single, root, True)
                if not target:
                    return {'error': self.error(self.ERROR_INV_PARAMS)}
                elif not self.__isAllowed(target, 'read'):
                    return {'error': self.error(self.ERROR_PERM_DENIED)}
                else:
                    path = target
                size += self.__dirSize(path, True)
            return {'size': size}
        else:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        
    def __checkName(self, name):
        """Check for valid file/dir name"""
        pattern = r'[\/\\\:\<\>]'
        if re.search(pattern, name):
            return False
        return True
    
    def __mkdir(self, newDir, rootPath, username):
        """Create new directory"""
        try:
            # TODO: should change the access right for the user only
            os.mkdir(newDir, self._options['dirMode'])
            user = pwd.getpwnam(username)
            os.chown(newDir, user.pw_uid, user.pw_gid)
            return {'added': [self.__cwd(newDir, rootPath)[0]]}
        except:
            return {'error': self.error(self.ERROR_MKDIR)}
    
    def mkdir(self, args):
        """Create new directory"""
        root = self.user.workspace
        name = args['name']
        username = self.user.username
        current = args['target']
        path = self.__findDir(current, root)
        newDir = os.path.join(path, name)

        if not path:
            return {'error': self.error(self.ERROR_MKDIR, self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(path, 'write'):
            return {'error': self.error(self.ERROR_MKDIR, self.ERROR_PERM_DENIED)}
        elif not self.__checkName(name):
            return {'error': self.error(self.ERROR_MKDIR, name, self.ERROR_INVALID_NAME)}
        elif os.path.exists(newDir):
            return {'error': self.error(self.ERROR_MKDIR, name, self.ERROR_EXISTS)}
        else:
            return self.__mkdir(newDir, root, username)
    
    def __mkfile(self, newFile, rootPath, username):
        """Create new file"""
        
        try:
            open(newFile, 'w').close()
            os.chmod(newFile, self._options['fileMode'])
            user = pwd.getpwnam(username)
            os.chown(newFile, user.pw_uid, user.pw_gid)
            return {'added': [self.__info(newFile, rootPath)]}
        except:
            return {'error': self.error(self.ERROR_MKFILE)}
    
    def mkfile(self, args):
        """Create new file"""
        root = self.user.workspace
        name = args['name']
        current = args['target']
        path = self.__findDir(current, root)
        newFile = os.path.join(path, name)
        username = self.user.username

        if not path:
            return {'error': self.error(self.ERROR_MKFILE, self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(path, 'write'):
            return {'error': self.error(self.ERROR_MKFILE, self.ERROR_PERM_DENIED)}
        elif not self.__checkName(name):
            return {'error': self.error(self.ERROR_MKFILE, name, self.ERROR_INVALID_NAME)}
        elif os.path.exists(newFile):
            return {'error': self.error(self.ERROR_MKFILE, name, self.ERROR_EXISTS)}
        else:
            return self.__mkfile(newFile, root, username)
    
    def __find(self, fhash, parent):
        """Find file/dir by hash"""
        fhash = str(fhash)
        if os.path.isdir(parent):
            for i in os.listdir(parent):
                path = os.path.join(parent, i)
                if fhash == self.__hash(path):
                    return path
        return None

    def __remove(self, target, rmList, erros):
        """Internal remove procedure"""
        
        if not self.__isAllowed(target, 'rm'):
            erros.append(self.ERROR_PERM_DENIED)
            return

        if not os.path.isdir(target):
            try:
                hash = self.__hash(target)
                os.unlink(target)
                rmList.append(hash)
                return
            except:
                erros.append(self.ERROR_RM)
                return
        else:
            for i in os.listdir(target):
                if self.__isAccepted(i):
                    self.__remove(os.path.join(target, i), rmList, erros)

            try:
                hash = self.__hash(target)
                os.rmdir(target)
                rmList.append(hash)
                return
            except:
                erros.append(self.ERROR_RM)
                return
    
    def rm(self, args):
        root = self.user.workspace
        
        if args['targets']:
            errors = []
            rmList = []
            for rm in args['targets']:
                target = self.__findDir(rm, root, True)
                if not target:
                    return {'error': self.error(self.ERROR_INV_PARAMS)}
                elif not self.__isAllowed(target, 'rm'):
                    return {'error': self.error(self.ERROR_PERM_DENIED)}
                else:
                    self.__remove(target, rmList, errors)
            if len(rmList):
                return {'removed': rmList}
            else:
                return {'error': errors}
        else:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
    
    def __rename(self, curName, newName, rootPath):
        """Rename file or dir"""
        try:
            os.rename(curName, newName)
            return {
                'removed': [self.__hash(curName)],
                'added': [self.__info(newName, rootPath)]
            }
        except:
            return {'error': self.error(self.ERROR_RENAME)}
    
    def rename(self, args):
        root = self.user.workspace
        target = self.__findDir(args['target'], root, True)
        name = args['name']
        
        if not target:
            return {'error': self.error(self.ERROR_FILE_NOT_FOUND)}

        # new add
        elif not self.__isAllowed(target, 'rename'):
            return {'error': self.error(self.ERROR_PERM_DENIED)}

        elif not self.__checkName(name):
            return {'error': self.error(self.ERROR_RENAME, name, self.ERROR_INVALID_NAME)}
        else:
            newName = os.path.dirname(target) + "/" + name
            if os.path.exists(newName):
                return {'error': self.error(self.ERROR_EXISTS)}
            else:
                return self.__rename(target, newName, root)
    
    def duplicate(self, args):
        pass
    
    def paste(self, args):
        pass
    
    def __fbuffer(self, f, chunk_size = _options['uploadWriteChunk']):
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            yield chunk
    
    def __isUploadAllow(self, name):
        allow = False
        deny = False
        mime = self.__mimetype(name)

        if 'all' in self._options['uploadAllow']:
            allow = True
        else:
            for a in self._options['uploadAllow']:
                if mime.find(a) == 0:
                    allow = True

        if 'all' in self._options['uploadDeny']:
            deny = True
        else:
            for d in self._options['uploadDeny']:
                if mime.find(d) == 0:
                    deny = True

        if self._options['uploadOrder'][0] == 'allow': # allow,deny
            if deny is True:
                return False
            elif allow is True:
                return True
            else:
                return False
        else: # deny,allow
            if allow is True:
                return True
            elif deny is True:
                return False
            else:
                return True
    
    def __upload(self, curDir, upFiles, rootPath, username):
        """Upload files"""
        user = pwd.getpwnam(username)
        result = {'added':[]}
        errors = []
        total = 0
        upSize = 0
        maxSize = self._options['uploadMaxSize'] * 1024 * 1024
        for file in upFiles:
            name = file.name
            if name:
                total += 1
                name = os.path.basename(name)
                if not self.__checkName(name):
                    self.__errorData(name, 'Invalid name')
                else:
                    name = os.path.join(curDir, name)
                    try:
                        f = open(name, 'wb', self._options['uploadWriteChunk'])
                        for chunk in file.chunks():
                            f.write(chunk)
                        f.close()
                        upSize += os.lstat(name).st_size
                        if self.__isUploadAllow(name):
                            os.chmod(name, self._options['fileMode'])
                            os.chown(name, user.pw_uid, user.pw_gid)
                            result['added'].append(self.__info(name, rootPath))
                        else:
                            errors.append((name, self.ERROR_UPLOAD_FILE_MIME))
                            try:
                                os.unlink(name)
                            except:
                                errors.append((name, self.ERROR_UPLOAD_FILE))
                    except:
                        errors.append((name, self.ERROR_UPLOAD_FILE))
                    if upSize > maxSize:
                        try:
                            os.unlink(name)
                            errors.append((name, self.ERROR_UPLOAD_FILE_SIZE))
                        except:
                            errors.append((name, self.ERROR_UPLOAD_FILE))
                        break

        if len(errors) == total:
            return {'error': self.error(self.ERROR_UPLOAD_FILE)}
        else:
            return result
    
    def upload(self, args):
        """Upload files"""
        root = self.user.workspace
        current = args['target']
        path = self.__findDir(current, root)
        upFiles = args['FILES']
        username = self.user.username

        if not path:
            return {'error': self.error(self.ERROR_UPLOAD, self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(path, 'write'):
            return {'error': self.error(self.ERROR_UPLOAD, self.ERROR_PERM_DENIED)}
        elif not upFiles:
            return {'error': self.error(self.ERROR_UPLOAD, self.ERROR_UPLOAD_NO_FILES)}
        else:
            return self.__upload(path, upFiles, root, username)        
    
    def hash(self, args):
        """get hash of the path"""
        root = self.user.workspace
        path = args['path']
        if self._options['rootAlias']:
            rootAlias = self._options['rootAlias']
            path = root + path[len(rootAlias):]
        
        return {'hash': self.__hash(path)}
    
    def __file_iterator(self, file_name, chunk_size=_options['uploadWriteChunk']):
        with open(file_name, mode='r', buffering=1) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    
    def file(self, args):
        root = self.user.workspace
        path = ''
        target = self.__findDir(args['target'], root, True)
        if not target:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(target, 'read'):
            return {'error': self.error(self.ERROR_PERM_DENIED)}
        else:
            path = target
            
        download = args.has_key('download') and args['download'] == '1'
        if download:
            if isinstance(path, unicode):
                path = path.encode(encoding='utf-8', errors='ignore')
            response = StreamingHttpResponse(self.__file_iterator(path))
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format(os.path.basename(path))

            return response
        else:
            return {}

    def preview(self, args):
        response = {}
        root = self.user.workspace
        target = self.__findDir(args['target'], root, True)
        if not target:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(target, 'read'):
            return {'error': self.error(self.ERROR_PERM_DENIED)}
        else:
            path = target

        fp = self.__get(path)
        response['data'] = base64.b64encode(fp)
        response['type'] = target.split('.')[-1]
        return response
    
    def __get(self, curFile):
        return open(curFile, 'r').read()
    
    def get(self, args):
        root = self.user.workspace
        path = ''
        target = self.__findDir(args['target'], root, True)
        if not target:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(target, 'read'):
            return {'error': self.error(self.ERROR_PERM_DENIED)}
        else:
            path = target
            
        return {'content': self.__get(path)}
    
    def __put(self, curFile, root, content):
        """Save content in file"""
        try:
            f = open(curFile, 'w+')
            f.write(content)
            f.close()
            return {'changed': [self.__info(curFile, root)]}
        except:
            return {'error': self.error(self.ERROR_SAVE)}
        
    def put(self, args):
        root = self.user.workspace
        path = ''
        target = self.__findDir(args['target'], root, True)
        if not target:
            return {'error': self.error(self.ERROR_INV_PARAMS)}
        elif not self.__isAllowed(target, 'write'):
            return {'error': self.error(self.ERROR_PERM_DENIED)}
        else:
            path = target
            
        return self.__put(path, root, args['content'])

    def __getarcname(self, targetList):
        resNotFound = {"name": '', 'error': self.error(self.ERROR_ARCHIVE_EXEC, self.ERROR_FILE_NOT_FOUND)}
        resPermDenied = {"name": '', 'error': self.error(self.ERROR_ARCHIVE, self.ERROR_PERM_DENIED)}
        if len(targetList) == 1:
            target = targetList[0]
            if os.path.isdir(target):
                if self.__isAllowed(target, 'read'):
                    res = {"name": os.path.basename(target), 'error': ''}
                else:
                    res = resPermDenied
            elif os.path.isfile(target):
                if self.__isAllowed(target, 'read'):
                    arcName_tmp = os.path.basename(target)
                    res = {"name": os.path.splitext(arcName_tmp)[0], 'error': ''}
                else:
                    res = resPermDenied
            else:
                res = resNotFound
        else:
            for target in targetList:
                if not os.path.isdir(target) and not os.path.isfile(target):
                    return resNotFound
                elif not self.__isAllowed(target, 'read'):
                    return resPermDenied
            res = {"name": str(datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')), 'error': ''}
        return res

    def archive(self, args):
        root = self.user.workspace
        username = self.user.username
        type = args['type']
        targetList = []

        if args['targets']:
            for element in args['targets']:
                element_path = self.__findDir(element, root, True)
                if not element_path:
                    return {'error': self.error(self.ERROR_INV_PARAMS)}
                elif not self.__isAllowed(element_path, 'read'):
                    return {'error': self.error(self.ERROR_PERM_DENIED)}
                else:
                    targetList.append(element_path)
            if len(targetList) == 0:
                return {'error': self.error(self.ERROR_INV_PARAMS)}
        else:
            return {'error': self.error(self.ERROR_INV_PARAMS)}

        arcRes = self.__getarcname(targetList)
        arcName = arcRes["name"]
        arcPathArr = targetList[0].split("/")
        arcPath = '/'.join(arcPathArr[0:len(arcPathArr) - 1])
        if arcName == "":
            return {'error': arcRes["error"]}
        elif type == "application/x-gzip":
            archive_path = os.path.join(arcPath, arcName + ".tar.gz")
        elif type == "application/x-tar":
            archive_path = os.path.join(arcPath, arcName + ".tar")
        elif type == "application/zip":
            archive_path = os.path.join(arcPath, arcName + ".zip")
        else:
            return {'error': self.error(self.ERROR_ARCHIVE_EXEC, type, self.ERROR_ARCHIVE_TYPE)}

        if not self.__isAllowed(root, 'write'):
            return {'error': self.error(self.ERROR_ARCHIVE, self.ERROR_PERM_DENIED)}
        elif os.path.isfile(archive_path):
            return {'error': self.error(self.ERROR_ARCHIVE, self.ERROR_EXISTS,
                                        os.path.basename(archive_path))}
        else:
            return self.__archive(targetList, archive_path, username, type)

    def __archive(self, targetList, archive_path, username, type):
        user = pwd.getpwnam(username)
        pathArr = str(archive_path).split("/")
        path = '/'.join(pathArr[0:len(pathArr)-1])
        try:
            if type == "application/zip":
                for target in targetList:
                    if os.path.isfile(target):
                        with zipfile.ZipFile(archive_path, 'a') as z:
                            to_file = target.split(path)[1]
                            z.write(target, to_file)
                    else:
                        with zipfile.ZipFile(archive_path, 'a') as z:
                            for root, dirs, files in os.walk(target):
                                for single_file in files:
                                    # if single_file != archive_path:
                                    filepath = os.path.join(root, single_file)
                                    to_file = filepath.split(path)[1]
                                    z.write(filepath, to_file)
            elif type == "application/x-gzip" or type == "application/x-tar":
                for target in targetList:
                    if os.path.isfile(target):
                        with tarfile.open(archive_path, 'a') as tar:
                            to_file = target.split(path)[1]
                            tar.add(target, arcname=to_file)
                    else:
                        with tarfile.open(archive_path, 'a') as tar:
                            for root, dirs, files in os.walk(target):
                                for single_file in files:
                                    # if single_file != archive_file:
                                    filepath = os.path.join(root, single_file)
                                    to_file = filepath.split(path)[1]
                                    tar.add(filepath, arcname=to_file)
            else:
                return {'error': self.error(self.ERROR_ARCHIVE_EXEC, self.ERROR_ARCHIVE_TYPE)}

            os.chmod(archive_path, self._options['fileMode'])
            os.chown(archive_path, user.pw_uid, user.pw_gid)
            return {'added': [self.__info(archive_path, archive_path)]}
        except:
            if os.path.isfile(archive_path):
                os.remove(archive_path)
            return {'error': self.error(self.ERROR_ARCHIVE_EXEC)}

    def extract(self, args):
        root = self.user.workspace
        username = self.user.username
        target = self.__findDir(args['target'], root, True)
        pathArr = str(target).split("/")
        path = '/'.join(pathArr[0:len(pathArr)-1])

        gzip_dir = re.findall(r'(.+?).tar.gz$', target)
        tar_dir = re.findall(r'(.+?).tar$', target)
        zip_dir = re.findall(r'(.+?).zip$', target)
        if len(gzip_dir) == 1:
            extract_dir = gzip_dir[0]
        elif len(tar_dir) == 1:
            extract_dir = tar_dir[0]
        elif len(zip_dir) == 1:
            extract_dir = zip_dir[0]
        else:
            return {'error': self.error(self.ERROR_EXTRACT_EXEC, target, self.ERROR_EXTRACT_TYPE)}

        if not os.path.isfile(target):
            return {'error': self.error(self.ERROR_EXTRACT, target, self.ERROR_FILE_NOT_FOUND)}
        elif not self.__isAllowed(target, 'read'):
            return {'error': self.error(self.ERROR_EXTRACT, self.ERROR_PERM_DENIED)}
        elif not self.__isAllowed(path, 'write'):
            return {'error': self.error(self.ERROR_EXTRACT, self.ERROR_PERM_DENIED)}
        elif os.path.isdir(extract_dir):
            return {'error': self.error(self.ERROR_EXTRACT, os.path.basename(target),
                                        self.ERROR_EXISTS, os.path.basename(extract_dir))}
        else:
            return self.__extract(target, extract_dir, username)

    def __extract(self, target, extract_dir, username):
        user = pwd.getpwnam(username)

        try:
            os.mkdir(extract_dir, self._options['dirMode'])
            os.chown(extract_dir, user.pw_uid, user.pw_gid)

            if zipfile.is_zipfile(target):
                file_zip_obj = zipfile.ZipFile(target)
                file_zip_obj.extractall(extract_dir)
                file_zip_obj.close()
            elif tarfile.is_tarfile(target):
                file_tar_obj = tarfile.open(target)
                file_tar_obj.extractall(extract_dir)
                file_tar_obj.close()
            else:
                if os.path.isdir(extract_dir):
                    os.remove(extract_dir)
                return {'error': self.error(self.ERROR_UNKNOWN, extract_dir, self.ERROR_EXTRACT_TYPE)}

            for path, dirs, files in os.walk(extract_dir, topdown=True):
                os.chown(path, user.pw_uid, user.pw_gid)
                for name in files:
                    os.chown(os.path.join(path, name), user.pw_uid, user.pw_gid)
            return {'added': [self.__info(extract_dir, extract_dir)]}
        except:
            if os.path.isdir(extract_dir):
                os.remove(extract_dir)
            return {'error': self.error(self.ERROR_EXTRACT_EXEC)}

    def __search(self, query, path, rootPath, result):
        """Search directories/files by query string"""
        for d in os.listdir(path):
            pd = os.path.join(path, d)
            if query in pd:
                result.append(self.__info(pd, rootPath))
            
            if os.path.isdir(pd) and self.is_readable(pd):
                self.__search(query, pd, rootPath, result)
    
    def search(self, args):
        root = self.user.workspace
        query = args['q']
        result = []
        if self.is_readable(root):
            self.__search(query, root, root, result)
        
        return {'files': result}
    
    def info(self, args):
        pass
    
    def dim(self, args):
        pass
    
    def resize(self, args):
        pass
    
    def netmount(self, args):
        pass
