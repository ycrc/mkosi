# SPDX-License-Identifier: LGPL-2.1-or-later

from collections.abc import Iterable
from typing import Any

from mkosi.context import Context
from mkosi.distribution import Distribution, join_mirror, rhel
from mkosi.installer.dnf import Dnf
from mkosi.installer.rpm import RpmRepository, setup_rpm


class Installer(rhel.Installer, distribution=Distribution.yalecrc):
    @classmethod
    def pretty_name(cls) -> str:
        return "Yale CRC"

    @classmethod
    def setup(cls, context: Context) -> None:
        setup_rpm(context, dbpath=cls.dbpath(context))
        Dnf.setup(context, list(cls.repositories(context)))

    @classmethod
    def repository_variants(
        cls,
        context: Context,
        gpgurls: tuple[str, ...],
        repo: str,
    ) -> Iterable[RpmRepository]:
        if context.config.local_mirror:
            yield RpmRepository(repo, f"baseurl={context.config.local_mirror}", gpgurls)
        else:
            minor = context.config.release.partition(".")[2]
            if minor in ["", "10"] or int(minor) % 2 == 1:
                mirror = context.config.mirror or "https://cdn.redhat.com/content/dist/"
            else:
                mirror = context.config.mirror or "https://cdn.redhat.com/content/eus/"

            common: dict[str, Any] = dict(
                gpgurls=gpgurls,
                sslcacert=cls.sslcacert(context),
                sslclientcert=cls.sslclientcert(context),
                sslclientkey=cls.sslclientkey(context),
            )

            v = context.config.release
            major = cls.major_release(context.config)
            yield RpmRepository(
                repo,
                f"baseurl={join_mirror(mirror, f'rhel{major}/{v}/$basearch/{repo}/os')}",
                enabled=True,
                **common,
            )
