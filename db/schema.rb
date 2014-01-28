# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20140128192817) do

  create_table "asignaturas", force: true do |t|
    t.string   "nombre_corto"
    t.string   "nombre_largo"
    t.text     "descripcion"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.string   "etiquetas"
  end

  create_table "examen", force: true do |t|
    t.string   "nombre"
    t.string   "etiquetas"
    t.string   "directorio"
    t.integer  "cantidad"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "asignatura_id"
  end

  create_table "examen_pregunta", force: true do |t|
    t.integer "examan_id"
    t.integer "preguntum_id"
  end

  create_table "listados", force: true do |t|
    t.integer  "asignatura_id"
    t.text     "estudiantes"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "opcions", force: true do |t|
    t.integer  "preguntum_id"
    t.text     "titulo"
    t.boolean  "right"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "pregunta", force: true do |t|
    t.text     "titulo"
    t.integer  "asignatura_id"
    t.string   "etiquetas"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "users", force: true do |t|
    t.string   "email",                  default: "", null: false
    t.string   "encrypted_password",     default: "", null: false
    t.string   "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.integer  "sign_in_count",          default: 0,  null: false
    t.datetime "current_sign_in_at"
    t.datetime "last_sign_in_at"
    t.string   "current_sign_in_ip"
    t.string   "last_sign_in_ip"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  add_index "users", ["email"], name: "index_users_on_email", unique: true
  add_index "users", ["reset_password_token"], name: "index_users_on_reset_password_token", unique: true

end
