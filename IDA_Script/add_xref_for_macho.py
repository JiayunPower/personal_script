import idc
import idautils

is64 = get_inf_structure().is_64bit()
ptsize = 8 if is64 else 4
GetPointer = Qword if is64 else Dword

def addxref(sel, f_ea):
    add_cref(sel, f_ea, XREF_USER | fl_F)
    add_cref(f_ea, sel, XREF_USER | fl_F)

def addobjcref():
    sel_map = {}
    imp_map = {}
    forbit_meth = set([
        ".cxx_construct",
        ".cxx_destruct",
        "alloc",
        "allowsWeakReference",
        "allocWithZone:",
        "autoContentAccessingProxy",
        "autorelease",
        "awakeAfterUsingCoder:",
        "beginContentAccess",
        "class",
        "classForCoder",
        "conformsToProtocol:",
        "copy",
        "copyWithZone:",
        "dealloc",
        "description",
        "debugDescription",
        "discardContentIfPossible",
        "doesNotRecognizeSelector:",
        "encodeWithCoder:",
        "endContentAccess",
        "finalize",
        "forwardingTargetForSelector:",
        "forwardInvocation:",
        "hash",
        "init",
        "initWithCoder:",
        "initialize",
        "instanceMethodForSelector:",
        "instanceMethodSignatureForSelector:",
        "instancesRespondToSelector:",
        "isContentDiscarded",
        "isEqual:",
        "isKindOfClass:",
        "isMemberOfClass:",
        "isProxy",
        "isSubclassOfClass:",
        "load",
        "methodForSelector:",
        "methodSignatureForSelector:",
        "mutableCopy",
        "mutableCopyWithZone:",
        "new",
        "performSelector:",
        "performSelector:withObject:",
        "performSelector:withObject:withObject:",
        "release",
        "replacementObjectForCoder:",
        "resolveClassMethod:",
        "resolveInstanceMethod:",
        "respondsToSelector:",
        "retain",
        "retainCount",
        "retainWeakReference",
        "self",
        "setVersion:",
        "superclass",
        "supportsSecureCoding",
        "version",
        "zone",
    ])
    # find the segment which contains objc method names
    seg = ida_segment.get_segm_by_name("__objc_selrefs")
    if not seg:
        print("cannot find __objc_selrefs")
        return
    for selref_ea in range(seg.start_ea, seg.end_ea, ptsize):
        sel_ea = GetPointer(selref_ea)
        sel_name = GetString(sel_ea)
        if sel_name not in forbit_meth:
            sel_map[sel_name] = sel_ea
    # get objc func table
    for addr in idautils.Functions():
        func_name = get_name(addr)
        if len(func_name) >= 6 and func_name[1] == "[": # +[? ?] -[? ?]
            sel_name = func_name[2:-1].split(" ")[-1]
            # may be more than one function with same sel but differenct class
            if sel_name not in imp_map:
                imp_map[sel_name] = []
            imp_map[sel_name].append(addr)
    # make xref
    for (sel_name, sel_ea) in sel_map.items():
        if sel_name in imp_map:
            for f_addr in imp_map[sel_name]:
                addxref(sel_ea, f_addr)
            print "added xref for " + sel_name

if __name__ == "__main__":
    addobjcref()

