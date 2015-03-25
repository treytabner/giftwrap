#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2015, Paul Czarkowski <paul@paulcz.net>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations

import argparse
import logging
import os
import subprocess
import sys
import yaml
import git
import time

def read_manifest(manifest):
    try:
        if os.path.isfile(manifest):
            return yaml.load(open(manifest, 'r'))
    except:
        print "Could not load manifest - %s" % manifest

def _set_envvar(key, value):
        os.environ[key] = value

def _mkdir(dir):
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

def _get_build_number(manifest):
    manifest_dir = os.path.dirname(manifest)
    g = git.cmd.Git(manifest_dir)
    try:
        return g.rev_list('HEAD','--count')
    except:
        return 1

def _run_command(command):
    print "Running command: %s" % " ".join(command)
    start_time = int(time.time())
    proc = subprocess.Popen(command, env=os.environ.copy(),
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    for line in iter(proc.stdout.readline, b''):
        print line.rstrip()

    finish_time = int(time.time())

    if proc.returncode:
        raise Exception("Failed to run %s with environment: %s"
                        % " ".join(command), os.environ)
        return proc.returncode
    else:
        print "command took %d seconds" % ( finish_time - start_time)
        return 0


def docker_builder(args):
    manifest = read_manifest(args.manifest)
    manifest_dir = os.path.abspath(args.manifest)
    package_dir = manifest['settings']['output_dir']
    _mkdir(package_dir)

    docker_build_command = [
        'docker', 'build', '--force-rm=true',
        '-t', '%s/giftwrapper' % ( args.os ),
        'dockerfiles/%s' % ( args.os )
    ]
    docker_build = _run_command(docker_build_command)

    docker_run_command = [
        'docker', 'run', '-t', '--rm', '-v',
        '%s:/tmp/manifest.yml' % os.path.abspath(args.manifest),
        '-v',
        '%s:%s' % ( package_dir, package_dir ),
        '%s/giftwrapper' % ( args.os ),
        'giftwrap', 'build',
        '-m', '/tmp/manifest.yml',
        '-v', '10.0-bbc%s' % ( args.build_number ),
        '-t', 'package'
    ]
    docker_run = _run_command(docker_run_command)

    if args.post_build_script:
        post_build_execute = _run_command(args.post_build_script)




def vagrant_builder(args):
    manifest = read_manifest(args.manifest)
    manifest_dir = os.path.abspath(args.manifest)

    _set_envvar("GIFTWRAP_ARGS", "-v 10.0-bbc%s -t package" % args.build_number)
    _set_envvar("GIFTWRAP_MANIFEST", args.manifest)
    if args.post_build_script:
        _set_envvar("GIFTWRAP_POSTBUILD_SCRIPT", args.post_build_script)

    vagrant_up_command = [ 'vagrant', 'up' ]
    vagrant_up = _run_command(vagrant_up_command)

    vagrant_destroy_command = [ 'vagrant', 'destroy', '-f' ]
    vagrant_destroy = _run_command(vagrant_destroy_command)

def main():
    parser = argparse.ArgumentParser(description='wrapper for CI to do giftwrap builds')
    parser.add_argument('--manifest', help='The full path to the giftwrap manifest', required=True)
    parser.add_argument('--method', help='The build method to use.', choices=["vagrant", "docker"], default="vagrant")
    parser.add_argument('--os', help='The OS to build for.', choices=["trusty", "precise"], default="precise")
    parser.add_argument('--post-build-script', help='The full path to a post build script')
    parser.add_argument('--build-number', help='The build number.', default='')

    args, extra_args = parser.parse_known_args()

    #print os.path.dirname(os.path.abspath(__file__))

    try:
        if not args.build_number:
            args.build_number = _get_build_number(args.manifest)
        print "--> Building %s with %s" % ( args.manifest, args.method )
        if args.method == 'vagrant':
            vagrant_builder(args)
        if args.method == 'docker':
            docker_builder(args)
    except Exception as e:
        print "something went wrong: %s" % (e)
        sys.exit(-1)

if __name__ == '__main__':
    main()

