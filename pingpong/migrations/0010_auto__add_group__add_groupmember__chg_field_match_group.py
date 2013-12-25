# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Group'
        db.create_table(u'pingpong_group', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Category'])),
            ('table', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Table'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'pingpong', ['Group'])

        # Adding model 'GroupMember'
        db.create_table(u'pingpong_groupmember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Player'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='members', to=orm['pingpong.Group'])),
            ('place', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('leader', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'pingpong', ['GroupMember'])


        # Changing field 'Match.group'
        db.alter_column(u'pingpong_match', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pingpong.Group'], null=True))

    def backwards(self, orm):
        # Deleting model 'Group'
        db.delete_table(u'pingpong_group')

        # Deleting model 'GroupMember'
        db.delete_table(u'pingpong_groupmember')


        # Changing field 'Match.group'
        db.alter_column(u'pingpong_match', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['group.Group'], null=True))

    models = {
        u'bracket.bracket': {
            'Meta': {'object_name': 'Bracket'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'bracket.bracketslot': {
            'Meta': {'object_name': 'BracketSlot'},
            'bracket': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bracket.Bracket']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'loser_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'loser_set'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"}),
            'match_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'match_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'no_player': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Player']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'}),
            'winner_goes_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'winner_set'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"})
        },
        u'pingpong.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_age': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'pingpong.double': {
            'Meta': {'object_name': 'Double', '_ormbases': [u'pingpong.Player']},
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pingpong.Player']"}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['pingpong.Player']"}),
            u'player_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pingpong.Player']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'pingpong.group': {
            'Meta': {'object_name': 'Group'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Table']", 'null': 'True', 'blank': 'True'})
        },
        u'pingpong.groupmember': {
            'Meta': {'object_name': 'GroupMember'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'members'", 'to': u"orm['pingpong.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'place': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Player']"})
        },
        u'pingpong.match': {
            'Meta': {'object_name': 'Match'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pingpong.Group']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['pingpong.Player']"}),
            'player1_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"}),
            'player1_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['pingpong.Player']"}),
            'player2_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"}),
            'player2_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'table': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'all_matches'", 'null': 'True', 'to': u"orm['pingpong.Table']"})
        },
        u'pingpong.player': {
            'Meta': {'object_name': 'Player'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'players'", 'null': 'True', 'to': u"orm['pingpong.Category']"}),
            'club': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'pingpong.table': {
            'Meta': {'object_name': 'Table'},
            'display_order': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['pingpong']