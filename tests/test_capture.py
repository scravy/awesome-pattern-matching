from __future__ import annotations

import unittest

from apm import *


class CaptureTest(unittest.TestCase):

    def test_multi_capture(self):
        result = match(
            value=[{
                "first-name": "Jane",
                "last-name": "Doe",
            }, {
                "first-name": "John",
                "last-name": "Doe",
            }],
            pattern=Each({"first-name": Capture(..., name="first_names")}),
            multimatch=True,
        )
        self.assertTrue(result)
        self.assertEqual(["Jane", "John"], result['first_names'])

    def test_last_capture(self):
        result = match(
            multimatch=False,
            value=[{
                "first-name": "Jane",
                "last-name": "Doe",
            }, {
                "first-name": "John",
                "last-name": "Doe",
            }],
            pattern=Each({"first-name": Capture(..., name="first_name")})
        )
        self.assertTrue(result)
        self.assertEqual("John", result['first_name'])

    def test_syntactic_sugar_rshift_operator(self):
        result = match(sample_k8s_response, {
            "containers": Each({
                "image": _ >> 'image',
                "name": _ >> 'name',
                "ports": Each({
                    "containerPort": _ >> 'port'
                }),
            })
        })
        self.assertTrue(result)
        self.assertEqual('k8s.gcr.io/metrics-server/metrics-server:v0.4.1', result['image'])
        self.assertEqual('metrics-server', result['name'])
        self.assertEqual(4443, result['port'])

    def test_syntactic_sugar_rmatmul_operator(self):
        # noinspection PyUnresolvedReferences
        result = match(sample_k8s_response, {
            "containers": Each({
                "image": 'image' @ _,
                "name": 'name' @ _,
                "ports": Each({
                    "containerPort": 'port' @ _
                }),
            })
        })
        self.assertTrue(result)
        self.assertEqual('k8s.gcr.io/metrics-server/metrics-server:v0.4.1', result['image'])
        self.assertEqual('metrics-server', result['name'])
        self.assertEqual(4443, result['port'])

    def test_syntactic_sugar_underscore(self):
        result = match(sample_k8s_response, {
            "containers": Each({
                "image": _ >> 'image',
                "name": _ >> 'name',
                "ports": Each({
                    "containerPort": _ >> 'port'
                }),
            })
        })
        self.assertTrue(result)
        self.assertEqual('k8s.gcr.io/metrics-server/metrics-server:v0.4.1', result['image'])
        self.assertEqual('metrics-server', result['name'])
        self.assertEqual(4443, result['port'])

    def test_regex_bind_groups(self):
        result = match("abcdef", Regex(r"(?P<one>[a-c]+)(?P<two>[a-z]+)", bind_groups=True))
        self.assertTrue(result)
        self.assertEqual(result['one'], 'abc')
        self.assertEqual(result['two'], 'def')
        self.assertEqual(result.one, 'abc')
        self.assertEqual(result.two, 'def')

    def test_nested_capture(self):
        result = match([1, 2, 3, 4], [1, Many(...) >> 'x' >> 'y', 4])
        self.assertTrue(result)
        self.assertEqual([2, 3], result.x)
        self.assertEqual([2, 3], result.y)


sample_k8s_response = {
    "containers": [
        {
            "args": [
                "--cert-dir=/tmp",
                "--secure-port=4443",
                "--kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname",
                "--kubelet-use-node-status-port"
            ],
            "image": "k8s.gcr.io/metrics-server/metrics-server:v0.4.1",
            "imagePullPolicy": "IfNotPresent",
            "livenessProbe": {
                "failureThreshold": 3,
                "httpGet": {
                    "path": "/livez",
                    "port": "https",
                    "scheme": "HTTPS"
                },
                "periodSeconds": 10,
                "successThreshold": 1,
                "timeoutSeconds": 1
            },
            "name": "metrics-server",
            "ports": [
                {
                    "containerPort": 4443,
                    "name": "https",
                    "protocol": "TCP"
                }
            ],
            "readinessProbe": {
                "failureThreshold": 3,
                "httpGet": {
                    "path": "/readyz",
                    "port": "https",
                    "scheme": "HTTPS"
                },
                "periodSeconds": 10,
                "successThreshold": 1,
                "timeoutSeconds": 1
            },
            "resources": {},
            "securityContext": {
                "readOnlyRootFilesystem": True,
                "runAsNonRoot": True,
                "runAsUser": 1000
            },
            "terminationMessagePath": "/dev/termination-log",
            "terminationMessagePolicy": "File",
            "volumeMounts": [
                {
                    "mountPath": "/tmp",
                    "name": "tmp-dir"
                },
                {
                    "mountPath": "/var/run/secrets/kubernetes.io/serviceaccount",
                    "name": "metrics-server-token-2j86f",
                    "readOnly": True
                }
            ]
        }
    ],
    "dnsPolicy": "ClusterFirst",
    "enableServiceLinks": True,
    "nodeName": "ip-10-2-169-118.ec2.internal",
    "nodeSelector": {
        "kubernetes.io/os": "linux"
    },
    "priority": 2000000000,
    "priorityClassName": "system-cluster-critical",
    "restartPolicy": "Always",
    "schedulerName": "default-scheduler",
    "securityContext": {},
    "serviceAccount": "metrics-server",
    "serviceAccountName": "metrics-server",
    "terminationGracePeriodSeconds": 30,
    "tolerations": [
        {
            "effect": "NoExecute",
            "key": "node.kubernetes.io/not-ready",
            "operator": "Exists",
            "tolerationSeconds": 300
        },
        {
            "effect": "NoExecute",
            "key": "node.kubernetes.io/unreachable",
            "operator": "Exists",
            "tolerationSeconds": 300
        }
    ],
    "volumes": [
        {
            "emptyDir": {},
            "name": "tmp-dir"
        },
        {
            "name": "metrics-server-token-2j86f",
            "secret": {
                "defaultMode": 420,
                "secretName": "metrics-server-token-2j86f"
            }
        }
    ]
}
