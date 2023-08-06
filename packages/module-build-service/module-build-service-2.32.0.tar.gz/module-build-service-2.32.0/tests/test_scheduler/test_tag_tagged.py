# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
import mock
import pytest

from mock import patch

import module_build_service.messaging
import module_build_service.scheduler.handlers.repos
import module_build_service.scheduler.handlers.tags
import module_build_service.models
from tests import conf
from module_build_service.db_session import db_session

import koji


@pytest.mark.usefixtures("reuse_component_init_data")
class TestTagTagged:

    @mock.patch("module_build_service.models.ModuleBuild.from_tag_change_event")
    def test_no_matching_module(self, from_tag_change_event):
        """ Test that when a tag msg hits us and we have no match,
        that we do nothing gracefully.
        """
        from_tag_change_event.return_value = None
        msg = module_build_service.messaging.KojiTagChange(
            "no matches for this...", "2016-some-nonexistent-build", "artifact", "artifact-1.2-1")
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

    def test_no_matching_artifact(self):
        """ Test that when a tag msg hits us and we have no match,
        that we do nothing gracefully.
        """
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "artifact",
            "artifact-1.2-1",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo(self, create_builder, koji_get_session, dbg):
        """
        Test that newRepo is called in the expected times.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.get_by_id(db_session, 3)

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2
        for c in module_build.current_batch():
            if c.package == "perl-Tangerine":
                c.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
            elif c.package == "perl-List-Compare":
                c.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
            c.state = koji.BUILD_STATES["COMPLETE"]

        db_session.commit()

        # Tag the first component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg
        )
        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg
        )

        # newRepo should not be called, because there are still components
        # to tag.
        assert not koji_session.newRepo.called

        # Tag the second component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg
        )

        # newRepo should not be called, because the component has not been
        # tagged to final tag so far.
        assert not koji_session.newRepo.called

        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should be called now - all components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db_session.refresh(module_build)

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_still_building_components(
        self, create_builder, koji_get_session, dbg
    ):
        """
        Test that newRepo is called in the expected times.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.get_by_id(db_session, 3)
        module_build.batch = 2
        component = db_session.query(module_build_service.models.ComponentBuild).filter_by(
            package="perl-Tangerine", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["BUILDING"]
        component.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"

        db_session.commit()

        # Tag the perl-List-Compare component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the perl-List-Compare component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should not be called, because perl-List-Compare has not been
        # built yet.
        assert not koji_session.newRepo.called

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_failed_components(self, create_builder, koji_get_session, dbg):
        """
        Test that newRepo is called in the expected times.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.get_by_id(db_session, 3)

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2

        component = db_session.query(module_build_service.models.ComponentBuild).filter_by(
            package="perl-Tangerine", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["FAILED"]
        component.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"

        component = db_session.query(module_build_service.models.ComponentBuild).filter_by(
            package="perl-List-Compare", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["COMPLETE"]
        component.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"

        db_session.commit()

        # Tag the perl-List-Compare component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg
        )
        # Tag the perl-List-Compare component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should be called now - all successfully built
        # components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db_session.refresh(module_build)

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_multiple_batches_tagged(
        self, create_builder, koji_get_session, dbg
    ):
        """
        Test that newRepo is called just once and only when all components
        are tagged even if we tag components from the multiple batches in the
        same time.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.get_by_id(db_session, 3)
        module_build.batch = 2

        mbm = module_build_service.models.ComponentBuild.from_component_name(
            db_session, "module-build-macros", 3)
        mbm.tagged = False

        for c in module_build.current_batch():
            if c.package == "perl-Tangerine":
                c.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
            elif c.package == "perl-List-Compare":
                c.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
            c.state = koji.BUILD_STATES["COMPLETE"]

        db_session.commit()

        # Tag the first component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should not be called, because there are still components
        # to tag.
        assert not koji_session.newRepo.called

        # Tag the second component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the second component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should not be called, because there are still components
        # to tag.
        assert not koji_session.newRepo.called

        # Tag the component from first batch to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "module-build-macros",
            "module-build-macros-0.1-1.module+0+b0a1d1f7",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the component from first batch to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "module-build-macros",
            "module-build-macros-0.1-1.module+0+b0a1d1f7",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should be called now - all components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db_session.refresh(module_build)

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_build_time_only(self, create_builder, koji_get_session, dbg):
        """
        Test the component.build_time_only is respected in tag handler.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": koji.TASK_STATES["CLOSED"]}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.get_by_id(db_session, 3)

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            if c.package == "module-build-macros":
                c.nvr = "module-build-macros-0.1-1.module+0+b0a1d1f7"
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2
        component = db_session.query(module_build_service.models.ComponentBuild).filter_by(
            package="perl-Tangerine", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["COMPLETE"]
        component.build_time_only = True
        component.tagged = False
        component.tagged_in_final = False
        component.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"

        component = db_session.query(module_build_service.models.ComponentBuild).filter_by(
            package="perl-List-Compare", module_id=module_build.id).one()
        component.state = koji.BUILD_STATES["COMPLETE"]
        component.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"

        db_session.commit()

        # Tag the perl-Tangerine component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        assert not koji_session.newRepo.called
        # Tag the perl-List-Compare component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the perl-List-Compare component to final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # newRepo should be called now - all successfully built
        # components have been tagged.
        koji_session.newRepo.assert_called_once_with(
            "module-testmodule-master-20170219191323-c40c156c-build")

        # Refresh our module_build object.
        db_session.refresh(module_build)

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456

    @pytest.mark.parametrize('task_state, expect_new_repo', (
        (None, True),  # Indicates a newRepo task has not been triggered yet.
        (koji.TASK_STATES["CLOSED"], True),
        (koji.TASK_STATES["CANCELED"], True),
        (koji.TASK_STATES["FAILED"], True),
        (koji.TASK_STATES["FREE"], False),
        (koji.TASK_STATES["OPEN"], False),
        (koji.TASK_STATES["ASSIGNED"], False),
    ))
    @patch(
        "module_build_service.builder.GenericBuilder.default_buildroot_groups",
        return_value={"build": [], "srpm-build": []},
    )
    @patch("module_build_service.builder.KojiModuleBuilder.KojiModuleBuilder.get_session")
    @patch("module_build_service.builder.GenericBuilder.create_from_module")
    def test_newrepo_not_duplicated(
        self, create_builder, koji_get_session, dbg, task_state, expect_new_repo
    ):
        """
        Test that newRepo is not called if a task is already in progress.
        """
        koji_session = mock.MagicMock()
        koji_session.getTag = lambda tag_name: {"name": tag_name}
        koji_session.getTaskInfo.return_value = {"state": task_state}
        koji_session.newRepo.return_value = 123456
        koji_get_session.return_value = koji_session

        builder = mock.MagicMock()
        builder.koji_session = koji_session
        builder.buildroot_ready.return_value = False
        builder.module_build_tag = {
            "name": "module-testmodule-master-20170219191323-c40c156c-build"
        }
        create_builder.return_value = builder

        module_build = module_build_service.models.ModuleBuild.get_by_id(db_session, 3)
        assert module_build

        # Set previous components as COMPLETE and tagged.
        module_build.batch = 1
        for c in module_build.up_to_current_batch():
            c.state = koji.BUILD_STATES["COMPLETE"]
            c.tagged = True
            c.tagged_in_final = True

        module_build.batch = 2
        for c in module_build.current_batch():
            if c.package == "perl-Tangerine":
                c.nvr = "perl-Tangerine-0.23-1.module+0+d027b723"
            elif c.package == "perl-List-Compare":
                c.nvr = "perl-List-Compare-0.53-5.module+0+d027b723"
            c.state = koji.BUILD_STATES["COMPLETE"]

        if task_state is not None:
            module_build.new_repo_task_id = 123456

        db_session.commit()

        # Tag the first component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the first component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-Tangerine",
            "perl-Tangerine-0.23-1.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the second component to the buildroot.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c-build",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)
        # Tag the second component to the final tag.
        msg = module_build_service.messaging.KojiTagChange(
            "id",
            "module-testmodule-master-20170219191323-c40c156c",
            "perl-List-Compare",
            "perl-List-Compare-0.53-5.module+0+d027b723",
        )
        module_build_service.scheduler.handlers.tags.tagged(
            config=conf, msg=msg)

        # All components are tagged, newRepo should be called if there are no active tasks.
        if expect_new_repo:
            koji_session.newRepo.assert_called_once_with(
                "module-testmodule-master-20170219191323-c40c156c-build")
        else:
            assert not koji_session.newRepo.called

        # Refresh our module_build object.
        db_session.refresh(module_build)

        # newRepo task_id should be stored in database, so we can check its
        # status later in poller.
        assert module_build.new_repo_task_id == 123456
        koji_session.newRepo.reset_mock()
