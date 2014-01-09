# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Table.short_name'
        db.add_column(u'pingpong_table', 'short_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Table.short_name'
        db.delete_column(u'pingpong_table', 'short_name')


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
            'player1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_as_player1'", 'null': 'True', 'to': u"orm['pingpong.Player']"}),
            'player1_bracket_slot': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'to': u"orm['bracket.BracketSlot']"}),
            'player1_score': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'player2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'match_as_player2'", 'null': 'True', 'to': u"orm['pingpong.Player']"}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'short_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'})
        }
    }

    complete_apps = ['pingpong']