from kubernetes import client, config

config.load_kube_config()

namespaces= []

v1 = client.CoreV1Api()
namespace_list = v1.list_namespace().items
for ns in namespace_list:
    # ignore ns added to Istio
    if "maistra.io/member-of" in ns.metadata.labels and ns.metadata.labels["maistra.io/member-of"] == "istio-system-dmz":
        continue
    # only check ns in dmz
    if "zone" in ns.metadata.labels and ns.metadata.labels["zone"] == "dmz":
        namespaces.append(ns.metadata.name)

nw = client.NetworkingV1Api()
for n in namespaces:
    print(n + ":")
    netpol = nw.list_namespaced_network_policy(n)
    for np in netpol.items:
        print(np.metadata.name)
    print("")