# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Agencia'
        db.create_table(u'iamcast_agencia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], blank=True)),
            ('nombre', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60)),
            ('dominio', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, blank=True)),
            ('estado_creacion', self.gf('django.db.models.fields.CharField')(default='CI', max_length=2)),
            ('activa', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('fecha_inicio', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 3, 20, 0, 0))),
            ('idioma', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
        ))
        db.send_create_signal(u'iamcast', ['Agencia'])

        # Adding model 'PagoContrato'
        db.create_table(u'iamcast_pagocontrato', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item_title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('item_quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('item_currency_id', self.gf('django.db.models.fields.CharField')(default='ARS', max_length=3)),
            ('item_unit_price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=3)),
        ))
        db.send_create_signal(u'iamcast', ['PagoContrato'])

        # Adding model 'ContratoAgencia'
        db.create_table(u'iamcast_contratoagencia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('titulo', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('fecha_inicio', self.gf('django.db.models.fields.DateTimeField')()),
            ('fecha_fin', self.gf('django.db.models.fields.DateTimeField')()),
            ('estado', self.gf('django.db.models.fields.CharField')(default='PE', max_length=2)),
            ('agencia', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['iamcast.Agencia'])),
            ('pago', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['iamcast.PagoContrato'], unique=True)),
        ))
        db.send_create_signal(u'iamcast', ['ContratoAgencia'])


    def backwards(self, orm):
        # Deleting model 'Agencia'
        db.delete_table(u'iamcast_agencia')

        # Deleting model 'PagoContrato'
        db.delete_table(u'iamcast_pagocontrato')

        # Deleting model 'ContratoAgencia'
        db.delete_table(u'iamcast_contratoagencia')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'iamcast.agencia': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Agencia'},
            'activa': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dominio': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'blank': 'True'}),
            'estado_creacion': ('django.db.models.fields.CharField', [], {'default': "'CI'", 'max_length': '2'}),
            'fecha_inicio': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 3, 20, 0, 0)'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idioma': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'blank': 'True'})
        },
        u'iamcast.contratoagencia': {
            'Meta': {'ordering': "['-fecha_inicio']", 'object_name': 'ContratoAgencia'},
            'agencia': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['iamcast.Agencia']"}),
            'estado': ('django.db.models.fields.CharField', [], {'default': "'PE'", 'max_length': '2'}),
            'fecha_fin': ('django.db.models.fields.DateTimeField', [], {}),
            'fecha_inicio': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pago': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['iamcast.PagoContrato']", 'unique': 'True'}),
            'titulo': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'iamcast.pagocontrato': {
            'Meta': {'object_name': 'PagoContrato'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_currency_id': ('django.db.models.fields.CharField', [], {'default': "'ARS'", 'max_length': '3'}),
            'item_quantity': ('django.db.models.fields.IntegerField', [], {}),
            'item_title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'item_unit_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '3'})
        }
    }

    complete_apps = ['iamcast']