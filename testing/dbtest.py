from db_manip import dbmanager
jdb = dbmanager()

print jdb.create_db()

print jdb.create_host("10.10.12.1", "root", "password")
print jdb.create_host("10.10.12.2", "root", "password")
print jdb.create_host("10.10.12.3", "rot", "password")
print jdb.create_host("10.10.12.4", "root", "password")
print jdb.create_host("10.10.12.5", "root", "password")
print jdb.create_host("10.10.12.6", "root", "password")
print jdb.create_host("10.10.12.77", "root", "pad")

print jdb.modify_host_name("10.10.12.77", "10.10.12.7")
print jdb.modify_host_user("10.10.12.3", "root")
print jdb.modify_host_pass("10.10.12.7", "password")

print jdb.show_host("10.10.12.7")

print jdb.show_all()

print jdb.create_group("Alpha")
print jdb.create_group("Beta")
print jdb.create_group("Gqmma")

print jdb.modify_gname("Gqmma", "Gamma")

print jdb.attach("10.10.12.1", "Alpha")
print jdb.attach("10.10.12.2", "Alpha")
print jdb.attach("10.10.12.3", "Alpha")

print jdb.attach("10.10.12.4", "Beta")
print jdb.attach("10.10.12.5", "Beta")
print jdb.attach("10.10.12.6", "Beta")
print jdb.attach("10.10.12.7", "Beta")

print jdb.attach("10.10.12.1", "Gamma")
print jdb.attach("10.10.12.7", "Gamma")

print jdb.show_group("Alpha")
print jdb.show_group("Beta")
print jdb.show_group("Gamma")

print jdb.delete_host("10.10.12.7")
print jdb.delete_group("Alpha")
print jdb.detach("10.10.12.4", "Beta")

print jdb.show_group("Alpha")
print jdb.show_group("Beta")
print jdb.show_group("Gamma")

print jdb.show_all()
